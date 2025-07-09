import React, { useState, useRef } from 'react';
import { Upload, File, X, AlertCircle, CheckCircle, Loader, Paperclip } from 'lucide-react';

const InlineFileUpload = ({ onFileUploaded, className = "" }) => {
  const [uploading, setUploading] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [error, setError] = useState('');
  const fileInputRef = useRef(null);

  const handleFileSelect = (e) => {
    if (e.target.files && e.target.files[0]) {
      handleFiles(e.target.files);
    }
  };

  const handleFiles = async (files) => {
    const allowedTypes = [
      'application/pdf',
      'application/msword',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      'text/plain',
      'text/markdown'
    ];
    
    const maxSize = 10 * 1024 * 1024; // 10MB

    for (let file of files) {
      if (!allowedTypes.includes(file.type)) {
        setError(`File type not supported. Please upload PDF, DOC, DOCX, TXT, or MD files.`);
        return;
      }
      
      if (file.size > maxSize) {
        setError(`File too large. Maximum size is 10MB.`);
        return;
      }
    }

    setError('');
    setUploading(true);

    try {
      for (let file of files) {
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch('/api/agent/upload', {
          method: 'POST',
          body: formData
        });

        const data = await response.json();
        
        if (data.success) {
          const uploadedFile = {
            id: Date.now() + Math.random(),
            name: file.name,
            size: file.size,
            type: file.type,
            uploadedAt: new Date().toISOString(),
            path: data.data.filepath
          };
          
          setUploadedFiles(prev => [...prev, uploadedFile]);
          
          if (onFileUploaded) {
            onFileUploaded(uploadedFile);
          }
        } else {
          setError(data.error || 'Failed to upload file');
        }
      }
    } catch (error) {
      console.error('Upload error:', error);
      setError('Failed to upload file. Please try again.');
    } finally {
      setUploading(false);
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
  };

  const removeFile = (fileId) => {
    setUploadedFiles(prev => prev.filter(file => file.id !== fileId));
  };

  return (
    <div className={`relative ${className}`}>
      {/* Upload Button */}
      <input
        ref={fileInputRef}
        type="file"
        multiple
        onChange={handleFileSelect}
        accept=".pdf,.doc,.docx,.txt,.md"
        className="hidden"
        disabled={uploading}
      />
      <button
        onClick={() => fileInputRef.current?.click()}
        disabled={uploading}
        className="flex items-center justify-center p-3 text-green-700 hover:bg-green-50 rounded-full transition-colors disabled:opacity-50"
        title="Upload files for agent context"
      >
        {uploading ? (
          <Loader className="h-5 w-5 animate-spin" />
        ) : (
          <Paperclip className="h-5 w-5" />
        )}
      </button>

      {/* Files indicator badge */}
      {uploadedFiles.length > 0 && (
        <div className="absolute -top-1 -right-1 bg-green-600 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center">
          {uploadedFiles.length}
        </div>
      )}

      {/* Error Message - Positioned absolutely */}
      {error && (
        <div className="absolute bottom-full left-0 mb-2 w-64 flex items-center space-x-2 p-2 bg-red-50 border border-red-200 rounded-lg shadow-lg z-10">
          <AlertCircle className="h-4 w-4 text-red-500 flex-shrink-0" />
          <p className="text-xs text-red-700">{error}</p>
        </div>
      )}

      {/* Uploaded Files Dropdown - Positioned absolutely */}
      {uploadedFiles.length > 0 && (
        <div className="absolute bottom-full left-0 mb-2 w-72 bg-white border border-gray-200 rounded-lg shadow-lg z-10">
          <div className="p-3 space-y-2">
            <p className="text-xs text-gray-600 font-medium">Attached Files:</p>
            <div className="space-y-1 max-h-32 overflow-y-auto">
              {uploadedFiles.map((file) => (
                <div
                  key={file.id}
                  className="flex items-center justify-between p-2 bg-green-50 border border-green-200 rounded text-xs"
                >
                  <div className="flex items-center space-x-2 min-w-0 flex-1">
                    <File className="h-3 w-3 text-green-600 flex-shrink-0" />
                    <div className="min-w-0 flex-1">
                      <p className="font-medium text-gray-900 truncate">{file.name}</p>
                      <p className="text-gray-500">{formatFileSize(file.size)}</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-1 flex-shrink-0">
                    <CheckCircle className="h-3 w-3 text-green-600" />
                    <button
                      onClick={() => removeFile(file.id)}
                      className="p-1 text-gray-400 hover:text-red-600 transition-colors"
                    >
                      <X className="h-3 w-3" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default InlineFileUpload; 