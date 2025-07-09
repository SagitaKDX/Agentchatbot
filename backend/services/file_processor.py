import os
import json
import PyPDF2
import docx
from datetime import datetime
from typing import Dict, List, Optional
import hashlib

class FileProcessor:
    def __init__(self, upload_dir: str = "../uploads"):
        self.upload_dir = upload_dir
        self.processed_files = {}
        self.file_index = {}
        
    def extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text content from PDF files"""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                return text.strip()
        except Exception as e:
            print(f"Error extracting text from PDF {file_path}: {e}")
            return ""
    
    def extract_text_from_docx(self, file_path: str) -> str:
        """Extract text content from DOCX files"""
        try:
            doc = docx.Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text.strip()
        except Exception as e:
            print(f"Error extracting text from DOCX {file_path}: {e}")
            return ""
    
    def extract_text_from_txt(self, file_path: str) -> str:
        """Extract text content from TXT/MD files"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read().strip()
        except Exception as e:
            print(f"Error reading text file {file_path}: {e}")
            return ""
    
    def process_file(self, file_path: str, original_filename: str) -> Dict:
        """Process a single uploaded file and extract relevant information"""
        try:
            full_path = os.path.join(self.upload_dir, file_path)
            
            if not os.path.exists(full_path):
                raise FileNotFoundError(f"File not found: {full_path}")
            
            # Get file info
            file_size = os.path.getsize(full_path)
            file_extension = original_filename.split('.')[-1].lower()
            
            # Extract text based on file type
            extracted_text = ""
            if file_extension == 'pdf':
                extracted_text = self.extract_text_from_pdf(full_path)
            elif file_extension in ['docx', 'doc']:
                extracted_text = self.extract_text_from_docx(full_path)
            elif file_extension in ['txt', 'md']:
                extracted_text = self.extract_text_from_txt(full_path)
            
            # Generate file hash for deduplication
            with open(full_path, 'rb') as f:
                file_hash = hashlib.md5(f.read()).hexdigest()
            
            # Create processed file record
            processed_file = {
                'id': file_hash,
                'original_filename': original_filename,
                'file_path': file_path,
                'file_size': file_size,
                'file_type': file_extension,
                'extracted_text': extracted_text,
                'text_length': len(extracted_text),
                'processed_at': datetime.now().isoformat(),
                'word_count': len(extracted_text.split()) if extracted_text else 0,
                'summary': self._generate_summary(extracted_text),
                'keywords': self._extract_keywords(extracted_text)
            }
            
            # Store in memory index
            self.processed_files[file_hash] = processed_file
            self.file_index[original_filename] = file_hash
            
            return processed_file
            
        except Exception as e:
            print(f"Error processing file {file_path}: {e}")
            return {
                'error': str(e),
                'file_path': file_path,
                'original_filename': original_filename,
                'processed_at': datetime.now().isoformat()
            }
    
    def _generate_summary(self, text: str, max_length: int = 500) -> str:
        """Generate a simple summary of the text content"""
        if not text or len(text) <= max_length:
            return text
        
        # Simple summary: first few sentences up to max_length
        sentences = text.split('.')
        summary = ""
        for sentence in sentences:
            if len(summary + sentence + ".") <= max_length:
                summary += sentence + "."
            else:
                break
        
        return summary.strip() or text[:max_length] + "..."
    
    def _extract_keywords(self, text: str, max_keywords: int = 20) -> List[str]:
        """Extract basic keywords from text"""
        if not text:
            return []
        
        # Simple keyword extraction: most common meaningful words
        words = text.lower().split()
        
        # Filter out common stop words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 
            'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 
            'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that', 
            'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 
            'us', 'them', 'my', 'your', 'his', 'her', 'its', 'our', 'their'
        }
        
        # Count word frequency
        word_freq = {}
        for word in words:
            clean_word = ''.join(c for c in word if c.isalnum()).lower()
            if len(clean_word) > 3 and clean_word not in stop_words:
                word_freq[clean_word] = word_freq.get(clean_word, 0) + 1
        
        # Return top keywords
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, _ in sorted_words[:max_keywords]]
    
    def get_all_processed_files(self) -> List[Dict]:
        """Get all processed files"""
        return list(self.processed_files.values())
    
    def get_file_by_id(self, file_id: str) -> Optional[Dict]:
        """Get a specific processed file by ID"""
        return self.processed_files.get(file_id)
    
    def get_files_by_keywords(self, keywords: List[str]) -> List[Dict]:
        """Find files containing specific keywords"""
        matching_files = []
        keywords_lower = [k.lower() for k in keywords]
        
        for file_data in self.processed_files.values():
            file_keywords = [k.lower() for k in file_data.get('keywords', [])]
            text_lower = file_data.get('extracted_text', '').lower()
            
            # Check if any keyword matches
            if any(keyword in file_keywords or keyword in text_lower for keyword in keywords_lower):
                matching_files.append(file_data)
        
        return matching_files
    
    def delete_file(self, file_id: str) -> bool:
        """Delete a processed file from index and filesystem"""
        try:
            if file_id in self.processed_files:
                file_data = self.processed_files[file_id]
                file_path = os.path.join(self.upload_dir, file_data['file_path'])
                
                # Remove from filesystem if exists
                if os.path.exists(file_path):
                    os.remove(file_path)
                
                # Remove from indexes
                del self.processed_files[file_id]
                
                # Remove from filename index
                for filename, fid in list(self.file_index.items()):
                    if fid == file_id:
                        del self.file_index[filename]
                        break
                
                return True
            return False
        except Exception as e:
            print(f"Error deleting file {file_id}: {e}")
            return False
    
    def get_context_for_agent(self, query: str, max_files: int = 5) -> str:
        """Get relevant file content as context for agent queries"""
        query_keywords = query.lower().split()
        
        # Score files based on keyword relevance
        scored_files = []
        for file_data in self.processed_files.values():
            if 'error' in file_data:
                continue
                
            score = 0
            text_lower = file_data.get('extracted_text', '').lower()
            file_keywords = [k.lower() for k in file_data.get('keywords', [])]
            
            # Score based on keyword matches
            for keyword in query_keywords:
                if keyword in text_lower:
                    score += text_lower.count(keyword)
                if keyword in file_keywords:
                    score += 5  # Higher weight for extracted keywords
            
            if score > 0:
                scored_files.append((score, file_data))
        
        # Sort by score and take top files
        scored_files.sort(key=lambda x: x[0], reverse=True)
        top_files = scored_files[:max_files]
        
        # Build context string
        context_parts = []
        for _, file_data in top_files:
            context_parts.append(f"=== From file: {file_data['original_filename']} ===")
            context_parts.append(file_data.get('summary', file_data.get('extracted_text', '')[:1000]))
            context_parts.append("")
        
        return "\n".join(context_parts)

# Global instance
file_processor = FileProcessor() 