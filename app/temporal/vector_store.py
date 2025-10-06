"""Temporal vector storage for threat detection insights using Pinecone."""

import os
import logging
from typing import Any, Optional
from datetime import datetime
import pinecone
from sentence_transformers import SentenceTransformer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TemporalVectorStore:
    """
    Manages temporal storage and retrieval of threat detection insights.
    Uses Pinecone for vector storage with temporal metadata.
    """
    
    def __init__(
        self,
        index_name: str = "threat-insights",
        dimension: int = 384,  # all-MiniLM-L6-v2 dimension
        metric: str = "cosine"
    ):
        """
        Initialize the temporal vector store.
        
        Args:
            index_name: Name of the Pinecone index
            dimension: Vector dimension (384 for all-MiniLM-L6-v2)
            metric: Distance metric for similarity search
        """
        # Initialize Pinecone
        api_key = os.getenv("PINECONE_API_KEY")
        if not api_key:
            raise ValueError("PINECONE_API_KEY environment variable not set")
        
        pinecone.init(api_key=api_key, environment=os.getenv("PINECONE_ENVIRONMENT", "gcp-starter"))
        self.index_name = index_name
        self.dimension = dimension
        
        # Initialize embedding model (lightweight and fast)
        logger.info("Loading embedding model...")
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Create or connect to index
        self._initialize_index(metric)
        
        logger.info(f"Temporal vector store initialized with index: {index_name}")
    
    def _initialize_index(self, metric: str):
        """Create Pinecone index if it doesn't exist."""
        existing_indexes = pinecone.list_indexes()
        
        if self.index_name not in existing_indexes:
            logger.info(f"Creating new Pinecone index: {self.index_name}")
            pinecone.create_index(
                name=self.index_name,
                dimension=self.dimension,
                metric=metric
            )
        
        self.index = pinecone.Index(self.index_name)
        logger.info(f"Connected to index: {self.index_name}")
    
    def _create_embedding(self, text: str) -> list[float]:
        """Generate embedding vector from text."""
        embedding = self.embedder.encode(text, convert_to_tensor=False)
        return embedding.tolist()
    
    def _create_searchable_text(self, analysis: dict[str, Any]) -> str:
        """
        Create comprehensive searchable text from vision analysis.
        
        Args:
            analysis: Vision analysis dictionary
            
        Returns:
            Concatenated searchable text
        """
        parts = []
        
        # Add threat information
        threat_level = analysis.get('threat_level', 'none')
        parts.append(f"Threat level: {threat_level}")
        
        # Add detected threats
        threats = analysis.get('threats_detected', [])
        if threats:
            parts.append(f"Threats: {', '.join(threats)}")
        
        # Add weapon information
        weapon_type = analysis.get('weapon_type', 'none')
        if weapon_type != 'none':
            parts.append(f"Weapon detected: {weapon_type}")
        
        # Add people information
        people_count = analysis.get('people_count', 0)
        parts.append(f"People count: {people_count}")
        
        if analysis.get('unfamiliar_face'):
            parts.append("Unknown person detected")
        
        # Add description
        description = analysis.get('description', '')
        if description:
            parts.append(f"Scene: {description}")
        
        return " | ".join(parts)
    
    def upsert_analysis(
        self,
        camera_id: int,
        timestamp: float,
        frame_number: int,
        analysis: dict[str, Any],
        video_path: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> str:
        """
        Store a vision analysis with temporal metadata.
        
        Args:
            camera_id: Camera identifier
            timestamp: Timestamp in seconds from video start
            frame_number: Frame number in video
            analysis: Vision analysis dictionary
            video_path: Optional path to video file
            session_id: Optional session identifier
            
        Returns:
            Unique ID of the stored record
        """
        # Create unique ID
        record_id = f"cam{camera_id}_f{frame_number}_{int(timestamp*1000)}"
        
        # Create searchable text
        searchable_text = self._create_searchable_text(analysis)
        
        # Generate embedding
        embedding = self._create_embedding(searchable_text)
        
        # Prepare metadata
        metadata = {
            "camera_id": camera_id,
            "timestamp": timestamp,
            "frame_number": frame_number,
            "threat_level": analysis.get('threat_level', 'none'),
            "weapon_type": analysis.get('weapon_type', 'none'),
            "people_count": analysis.get('people_count', 0),
            "unfamiliar_face": analysis.get('unfamiliar_face', False),
            "threats": ",".join(analysis.get('threats_detected', [])),
            "description": analysis.get('description', '')[:1000],  # Pinecone metadata limit
            "searchable_text": searchable_text[:1000],
            "ingestion_time": datetime.now().isoformat()
        }
        
        if video_path:
            metadata["video_path"] = video_path
        
        if session_id:
            metadata["session_id"] = session_id
        
        # Upsert to Pinecone
        self.index.upsert(
            vectors=[{
                "id": record_id,
                "values": embedding,
                "metadata": metadata
            }]
        )
        
        logger.info(
            f"Upserted analysis: camera={camera_id}, "
            f"timestamp={timestamp:.1f}s, threat={metadata['threat_level']}"
        )
        
        return record_id
    
    def query_by_time_range(
        self,
        camera_id: int,
        start_time: float,
        end_time: float,
        top_k: int = 10
    ) -> list[dict[str, Any]]:
        """
        Query insights within a specific time range.
        
        Args:
            camera_id: Camera identifier
            start_time: Start timestamp in seconds
            end_time: End timestamp in seconds
            top_k: Maximum number of results
            
        Returns:
            List of matching insights with metadata
        """
        # Query with filters
        results = self.index.query(
            vector=[0] * self.dimension,  # Dummy vector for metadata-only query
            filter={
                "camera_id": {"$eq": camera_id},
                "timestamp": {"$gte": start_time, "$lte": end_time}
            },
            top_k=top_k,
            include_metadata=True
        )
        
        # Format results
        insights = []
        for match in results['matches']:
            insight = {
                "id": match['id'],
                "score": match['score'],
                **match['metadata']
            }
            insights.append(insight)
        
        # Sort by timestamp
        insights.sort(key=lambda x: x.get('timestamp', 0))
        
        logger.info(
            f"Found {len(insights)} insights for camera {camera_id} "
            f"between {start_time:.1f}s and {end_time:.1f}s"
        )
        
        return insights
    
    def query_by_semantic_search(
        self,
        query_text: str,
        camera_id: Optional[int] = None,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None,
        top_k: int = 5
    ) -> list[dict[str, Any]]:
        """
        Semantic search across stored insights.
        
        Args:
            query_text: Natural language query
            camera_id: Optional camera filter
            start_time: Optional start time filter
            end_time: Optional end time filter
            top_k: Maximum number of results
            
        Returns:
            List of most relevant insights
        """
        # Generate query embedding
        query_embedding = self._create_embedding(query_text)
        
        # Build filter
        filter_dict = {}
        if camera_id is not None:
            filter_dict["camera_id"] = {"$eq": camera_id}
        
        if start_time is not None and end_time is not None:
            filter_dict["timestamp"] = {"$gte": start_time, "$lte": end_time}
        
        # Execute query
        results = self.index.query(
            vector=query_embedding,
            filter=filter_dict if filter_dict else None,
            top_k=top_k,
            include_metadata=True
        )
        
        # Format results
        insights = []
        for match in results['matches']:
            insight = {
                "id": match['id'],
                "relevance_score": match['score'],
                **match['metadata']
            }
            insights.append(insight)
        
        logger.info(f"Semantic search found {len(insights)} relevant insights")
        
        return insights
    
    def query_by_threat_level(
        self,
        threat_level: str,
        camera_id: Optional[int] = None,
        limit: int = 20
    ) -> list[dict[str, Any]]:
        """
        Query insights by threat level.
        
        Args:
            threat_level: Threat level to search for
            camera_id: Optional camera filter
            limit: Maximum number of results
            
        Returns:
            List of matching insights
        """
        filter_dict = {"threat_level": {"$eq": threat_level}}
        
        if camera_id is not None:
            filter_dict["camera_id"] = {"$eq": camera_id}
        
        results = self.index.query(
            vector=[0] * self.dimension,
            filter=filter_dict,
            top_k=limit,
            include_metadata=True
        )
        
        insights = []
        for match in results['matches']:
            insight = {
                "id": match['id'],
                **match['metadata']
            }
            insights.append(insight)
        
        insights.sort(key=lambda x: x.get('timestamp', 0))
        
        logger.info(
            f"Found {len(insights)} insights with threat level: {threat_level}"
        )
        
        return insights
    
    def delete_by_session(self, session_id: str):
        """Delete all insights for a specific session."""
        self.index.delete(filter={"session_id": {"$eq": session_id}})
        logger.info(f"Deleted insights for session: {session_id}")
    
    def get_stats(self) -> dict[str, Any]:
        """Get statistics about stored data."""
        stats = self.index.describe_index_stats()
        return {
            "total_vectors": stats['total_vector_count'],
            "dimension": stats['dimension'],
            "index_fullness": stats.get('index_fullness', 0)
        }