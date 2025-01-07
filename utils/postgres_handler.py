import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Optional, List, Dict, Any, Union
import logging
from config import DB_CONNECTION_STRING

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PostgresHandler:
    def __init__(self, connection_string: str = DB_CONNECTION_STRING):
        self.connection_string = connection_string
        self.conn = None
        self.cursor = None

    def connect(self) -> None:
        """Establish connection to the database"""
        try:
            self.conn = psycopg2.connect( self.connection_string)
            self.cursor = self.conn.cursor(cursor_factory=RealDictCursor)
            logger.info(f"Successfully connected to the database")
        except psycopg2.Error as e:
            logger.error(f"Error connecting to the database: {e}")
            raise

    def disconnect(self) -> None:
        """Close database connection"""
        try:
            if self.cursor:
                self.cursor.close()
            if self.conn:
                self.conn.close()
                logger.info("Database connection closed")
        except psycopg2.Error as e:
            logger.error(f"Error closing database connection: {e}")
            raise

    def execute(self, query: str, params: Optional[tuple] = None) -> None:
        """Execute a query without returning results"""
        try:
            self.cursor.execute(query, params)
            self.conn.commit()
        except psycopg2.Error as e:
            self.conn.rollback()
            logger.error(f"Error executing query: {e}")
            raise

    def fetch_all(self, query: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """Execute a query and fetch all results"""
        try:
            self.cursor.execute(query, params)
            results = self.cursor.fetchall()
            return [dict(row) for row in results]
        except psycopg2.Error as e:
            logger.error(f"Error fetching results: {e}")
            raise

    def fetch_one(self, query: str, params: Optional[tuple] = None) -> Optional[Dict[str, Any]]:
        """Execute a query and fetch one result"""
        try:
            self.cursor.execute(query, params)
            result = self.cursor.fetchone()
            return dict(result) if result else None
        except psycopg2.Error as e:
            logger.error(f"Error fetching result: {e}")
            raise

    def execute_query(self, query: str) -> Dict[str, Any]:
        try:
            self.cursor.execute(query)
            results = self.cursor.fetchall()
            
            if not results:
                return {
                    "status": "no_results",
                    "message": "The query returned no results.",
                    "data": []
                }

            results_list = [dict(row) for row in results]
            
            if 'geometry_wkt' not in results_list[0]:
                return {
                    "status": "error",
                    "message": "The result set does not contain 'geometry_wkt'.",
                    "data": []
                }

            return {
                "status": "success",
                "data": results_list
            }

        except Exception as e:
            logger.error(f"Error executing simple query: {e}")
            return {
                "status": "error",
                "message": str(e),
                "data": []
            }

    def __enter__(self):
        """Context manager enter"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()