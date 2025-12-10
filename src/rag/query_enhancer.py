"""
Query Enhancement with HyDE and Multi-Query Generation.
Improves retrieval by transforming and expanding queries.
"""
from typing import List
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate

from src.config import GOOGLE_API_KEY, GEMINI_MODEL


class QueryEnhancer:
    """
    Query enhancement using HyDE (Hypothetical Document Embeddings)
    and multi-query generation for improved retrieval.
    """
    
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model=GEMINI_MODEL,
            google_api_key=GOOGLE_API_KEY,
            temperature=0.7
        )
        
        # HyDE prompt - generates hypothetical answer
        self.hyde_prompt = PromptTemplate(
            input_variables=["query"],
            template="""You are a SaaS customer support expert. Given the following customer question, 
write a detailed hypothetical answer that might appear in the support documentation.
Focus on being informative and using common support terminology.

Customer Question: {query}

Hypothetical Documentation Answer:"""
        )
        
        # Multi-query prompt - generates query variations
        self.multi_query_prompt = PromptTemplate(
            input_variables=["query"],
            template="""You are an AI assistant helping to improve search results.
Given the following customer question, generate 3 alternative phrasings that might help retrieve relevant support documentation.
Focus on different terminology, synonyms, and perspectives.

Original Question: {query}

Generate exactly 3 alternative queries, one per line, without numbering:"""
        )
    
    def generate_hyde_document(self, query: str) -> str:
        """
        Generate a hypothetical document using HyDE.
        The embedding of this document often retrieves better than the query itself.
        
        Args:
            query: Original user query
            
        Returns:
            Hypothetical document/answer
        """
        try:
            prompt = self.hyde_prompt.format(query=query)
            response = self.llm.invoke(prompt)
            return response.content
        except Exception as e:
            print(f"HyDE generation failed: {e}")
            return query  # Fallback to original query
    
    def generate_multi_queries(self, query: str) -> List[str]:
        """
        Generate multiple query variations for broader retrieval.
        
        Args:
            query: Original user query
            
        Returns:
            List of query variations (including original)
        """
        queries = [query]  # Always include original
        
        try:
            prompt = self.multi_query_prompt.format(query=query)
            response = self.llm.invoke(prompt)
            
            # Parse response into separate queries
            variations = [
                q.strip() 
                for q in response.content.strip().split('\n') 
                if q.strip()
            ]
            queries.extend(variations[:3])  # Limit to 3 variations
            
        except Exception as e:
            print(f"Multi-query generation failed: {e}")
        
        return queries
    
    def enhance_query(
        self,
        query: str,
        use_hyde: bool = True,
        use_multi_query: bool = True
    ) -> dict:
        """
        Enhance query using HyDE and/or multi-query generation.
        
        Args:
            query: Original user query
            use_hyde: Whether to generate HyDE document
            use_multi_query: Whether to generate query variations
            
        Returns:
            Dict with original query, hyde document, and query variations
        """
        result = {
            "original_query": query,
            "hyde_document": None,
            "query_variations": [query]
        }
        
        if use_hyde:
            result["hyde_document"] = self.generate_hyde_document(query)
        
        if use_multi_query:
            result["query_variations"] = self.generate_multi_queries(query)
        
        return result


# Default query enhancer instance
query_enhancer = QueryEnhancer()
