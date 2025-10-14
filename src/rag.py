import io
import zipfile
import requests
import frontmatter
import re
import os
from dotenv import load_dotenv
from openai import OpenAI
from minsearch import VectorSearch
from sentence_transformers import SentenceTransformer
from minsearch import Index
from tqdm.auto import tqdm
import numpy as np

load_dotenv()

class RAGChatbot:
    def __init__(self):
        self.client = OpenAI()
        self.embedding_model = None
        self.chunks = None
        self.embeddings = None
        self.repo_vindex = None

    def initialize(self, repo_owner='Rachel0619', repo_name='PickLLM'):
        """Initialize the chatbot by loading and processing repository data"""
        print(f"Initializing RAG chatbot with {repo_owner}/{repo_name}...")
        data = self._read_repo_data(repo_owner, repo_name)
        self.chunks = self._process_documents(data)
        self._build_index()
        print(f"✅ RAG chatbot initialized with {len(self.chunks)} chunks")

    def _read_repo_data(self, repo_owner, repo_name):
        """Read repository data from GitHub"""
        prefix = 'https://codeload.github.com'
        url = f'{prefix}/{repo_owner}/{repo_name}/zip/refs/heads/main'
        resp = requests.get(url)

        if resp.status_code != 200:
            raise Exception(f"Failed to download repository: {resp.status_code}")

        repository_data = []

        zf = zipfile.ZipFile(io.BytesIO(resp.content))

        for file_info in zf.infolist():
            filename = file_info.filename
            filename_lower = filename.lower()

            if not (filename_lower.endswith('.md')
                or filename_lower.endswith('.mdx')):
                continue

            try:
                with zf.open(file_info) as f_in:
                    content = f_in.read().decode('utf-8', errors='ignore')
                    post = frontmatter.loads(content)
                    data = post.to_dict()
                    data['filename'] = filename
                    repository_data.append(data)
            except Exception as e:
                print(f'Error processing {filename}: {e}')
                continue
        zf.close()
        return repository_data

    def _process_documents(self, data):
        """Process documents into chunks"""
        chunks = []
        for doc in data:
            doc_copy = doc.copy()
            doc_content = doc_copy.pop('content', '')
            if not doc_content:
                continue
            sections = self._split_markdown_by_level(doc_content, level=2)
            for section in sections:
                section_doc = doc_copy.copy()
                section_doc['section'] = section
                chunks.append(section_doc)
        return chunks

    def _split_markdown_by_level(self, text, level=2):
        """
        Split markdown text by a specific header level.

        :param text: Markdown text as a string
        :param level: Header level to split on
        :return: List of sections as strings
        """
        # This regex matches markdown headers
        # For level 2, it matches lines starting with "## "
        header_pattern = r'^(#{' + str(level) + r'} )(.+)$'
        pattern = re.compile(header_pattern, re.MULTILINE)

        # Split and keep the headers
        parts = pattern.split(text)

        sections = []
        for i in range(1, len(parts), 3):
            # We step by 3 because regex.split() with
            # capturing groups returns:
            # [before_match, group1, group2, after_match, ...]
            # here group1 is "## ", group2 is the header text
            header = parts[i] + parts[i+1]  # "## " + "Title"
            header = header.strip()

            # Get the content after this header
            content = ""
            if i+2 < len(parts):
                content = parts[i+2].strip()

            if content:
                section = f'{header}\n\n{content}'
            else:
                section = header
            sections.append(section)

        return sections

    def _build_index(self):
        """Build vector search index from chunks"""
        print("Building vector index...")
        self.embedding_model = SentenceTransformer('multi-qa-distilbert-cos-v1')
        embeddings = []
        for d in tqdm(self.chunks):
            v = self.embedding_model.encode(d['section'])
            embeddings.append(v)
        self.embeddings = np.array(embeddings)
        self.repo_vindex = VectorSearch()
        self.repo_vindex.fit(self.embeddings, self.chunks)
        print("✅ Vector index built successfully")

    def _vector_search(self, query, num_results=2):
        """Search for relevant context using vector similarity"""
        if self.repo_vindex is None or self.embedding_model is None:
            raise Exception("Chatbot not initialized. Call initialize() first.")
        q = self.embedding_model.encode(query)
        return self.repo_vindex.search(q, num_results=num_results)

    def _format_prompt(self, query, context):
        """Format the prompt for the LLM"""
        context_text = "\n\n".join([doc.get('section', '') for doc in context])
        return f"""
You are a friendly assistant for PickLLM, an AI-powered platform that helps users discover and compare Large Language Models.

Answer user questions in a conversational, concise way (2-3 sentences max). Be helpful and warm, but keep responses brief and to the point.

Question: {query}

Relevant context from PickLLM documentation:
{context_text}

Instructions:
- Answer directly and concisely
- Use the context provided to give accurate information
- If the context doesn't contain the answer, politely say you don't have that specific information
- Keep your response under 3 sentences when possible
        """.strip()

    def chat(self, query):
        """
        Main chat interface - takes a user query and returns a response
        """
        try:
            # Search for relevant context
            context = self._vector_search(query, num_results=2)

            # Format prompt and call LLM
            prompt = self._format_prompt(query, context)
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=150,
                temperature=0.7
            )

            return response.choices[0].message.content
        except Exception as e:
            print(f"Error in chat: {e}")
            return "I'm sorry, I encountered an error processing your question. Please try again."

if __name__ == "__main__":
    # Test the chatbot
    chatbot = RAGChatbot()
    chatbot.initialize('Rachel0619', 'PickLLM')

    # Test query
    query = "What data are you using to support the recommendation?"
    response = chatbot.chat(query)
    print(f"Q: {query}")
    print(f"A: {response}")
