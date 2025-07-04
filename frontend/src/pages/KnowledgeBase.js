import React, { useState, useEffect } from 'react';
import { Upload, FileText, Trash2, Eye, Download, Plus, File, BookOpen } from 'lucide-react';

const KnowledgeBase = () => {
  const [files, setFiles] = useState(() => {
    const saved = localStorage.getItem('englishAI_knowledgeBase');
    if (saved) {
      return JSON.parse(saved);
    }
    return [
      {
        id: 1,
        name: 'AI Vocabulary Guide.pdf',
        type: 'pdf',
        size: '2.3 MB',
        uploadDate: '2024-01-15',
        status: 'processed'
      },
      {
        id: 2,
        name: 'IoT Technical Terms.docx',
        type: 'docx',
        size: '1.8 MB',
        uploadDate: '2024-01-14',
        status: 'processed'
      },
      {
        id: 3,
        name: 'Chip Technology Lesson Plan.pdf',
        type: 'pdf',
        size: '1.2 MB',
        uploadDate: '2024-01-13',
        status: 'processed'
      }
    ];
  });
  const [dragActive, setDragActive] = useState(false);
  const [uploading, setUploading] = useState(false);

  // Save files to localStorage whenever they change
  useEffect(() => {
    localStorage.setItem('englishAI_knowledgeBase', JSON.stringify(files));
  }, [files]);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileUpload(e.dataTransfer.files);
    }
  };

  const handleFileUpload = async (fileList) => {
    setUploading(true);
    
    const newFiles = Array.from(fileList).map(file => ({
      id: Date.now() + Math.random(),
      name: file.name,
      type: file.name.split('.').pop().toLowerCase(),
      size: (file.size / (1024 * 1024)).toFixed(1) + ' MB',
      uploadDate: new Date().toISOString().split('T')[0],
      status: 'processing'
    }));

    setFiles(prev => [...newFiles, ...prev]);
    
    // Simulate processing time
    setTimeout(() => {
      setFiles(prev => prev.map(file => 
        newFiles.some(nf => nf.id === file.id) 
          ? { ...file, status: 'processed' } 
          : file
      ));
      setUploading(false);
    }, 2000);
  };

  const deleteFile = (fileId) => {
    setFiles(prev => prev.filter(file => file.id !== fileId));
  };

  const getFileIcon = (type) => {
    if (type === 'pdf') return <FileText className="h-5 w-5 text-red-500" />;
    if (type === 'docx' || type === 'doc') return <File className="h-5 w-5 text-blue-500" />;
    return <File className="h-5 w-5 text-gray-500" />;
  };

  const getStatusBadge = (status) => {
    if (status === 'processed') {
      return <span className="px-2 py-1 text-xs font-medium bg-green-100 text-green-800 rounded-full">Ready</span>;
    }
    if (status === 'processing') {
      return <span className="px-2 py-1 text-xs font-medium bg-yellow-100 text-yellow-800 rounded-full">Processing</span>;
    }
    return <span className="px-2 py-1 text-xs font-medium bg-gray-100 text-gray-800 rounded-full">Unknown</span>;
  };

  return (
    <div className="min-h-[calc(100vh-64px)] bg-gray-50">
      <div className="max-w-6xl mx-auto p-6">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center space-x-3 mb-4">
            <div className="w-10 h-10 bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl flex items-center justify-center">
              <BookOpen className="h-5 w-5 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Knowledge Base</h1>
              <p className="text-gray-600 mt-1">Upload and manage your teaching materials for Veron AI Agent</p>
            </div>
          </div>
        </div>

        {/* Upload Area */}
        <div className="mb-8">
          <div
            className={`relative border-2 border-dashed rounded-2xl p-8 text-center transition-all ${
              dragActive
                ? 'border-blue-500 bg-blue-50'
                : 'border-gray-300 hover:border-gray-400 bg-white'
            }`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
          >
            <div className="flex flex-col items-center">
              <div className="w-16 h-16 bg-gray-100 rounded-2xl flex items-center justify-center mb-4">
                <Upload className="h-8 w-8 text-gray-400" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                Upload your teaching materials
              </h3>
              <p className="text-gray-600 mb-4 max-w-md">
                Drag and drop your PDF or Word documents here, or click to browse files. 
                These will be used to enhance Veron's knowledge for better assistance.
              </p>
              <div className="flex flex-col sm:flex-row gap-3">
                <label className="bg-blue-600 text-white px-6 py-3 rounded-xl hover:bg-blue-700 transition-colors cursor-pointer font-medium">
                  Browse files
                  <input
                    type="file"
                    multiple
                    accept=".pdf,.doc,.docx"
                    onChange={(e) => handleFileUpload(e.target.files)}
                    className="hidden"
                  />
                </label>
                <div className="text-sm text-gray-500 self-center">
                  Supports PDF, DOC, DOCX files up to 10MB each
                </div>
              </div>
            </div>
            
            {uploading && (
              <div className="absolute inset-0 bg-white bg-opacity-90 flex items-center justify-center rounded-2xl">
                <div className="text-center">
                  <div className="w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-3"></div>
                  <p className="text-gray-600 font-medium">Processing files...</p>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Statistics */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white p-6 rounded-2xl border border-gray-200">
            <div className="flex items-center">
              <div className="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center">
                <FileText className="h-6 w-6 text-blue-600" />
              </div>
              <div className="ml-4">
                <p className="text-2xl font-bold text-gray-900">{files.length}</p>
                <p className="text-gray-600">Total Documents</p>
              </div>
            </div>
          </div>
          <div className="bg-white p-6 rounded-2xl border border-gray-200">
            <div className="flex items-center">
              <div className="w-12 h-12 bg-green-100 rounded-xl flex items-center justify-center">
                <BookOpen className="h-6 w-6 text-green-600" />
              </div>
              <div className="ml-4">
                <p className="text-2xl font-bold text-gray-900">{files.filter(f => f.status === 'processed').length}</p>
                <p className="text-gray-600">Ready for Use</p>
              </div>
            </div>
          </div>
          <div className="bg-white p-6 rounded-2xl border border-gray-200">
            <div className="flex items-center">
              <div className="w-12 h-12 bg-purple-100 rounded-xl flex items-center justify-center">
                <Plus className="h-6 w-6 text-purple-600" />
              </div>
              <div className="ml-4">
                <p className="text-2xl font-bold text-gray-900">
                  {files.reduce((acc, file) => acc + parseFloat(file.size), 0).toFixed(1)}
                </p>
                <p className="text-gray-600">Total Size (MB)</p>
              </div>
            </div>
          </div>
        </div>

        {/* Files List */}
        <div className="bg-white rounded-2xl border border-gray-200 overflow-hidden">
          <div className="p-6 border-b border-gray-200">
            <h2 className="text-xl font-semibold text-gray-900">Uploaded Documents</h2>
            <p className="text-gray-600 mt-1">Manage your teaching materials and resources</p>
          </div>
          
          {files.length === 0 ? (
            <div className="p-12 text-center">
              <div className="w-16 h-16 bg-gray-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
                <FileText className="h-8 w-8 text-gray-400" />
              </div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">No documents yet</h3>
              <p className="text-gray-600">Upload your first teaching material to get started</p>
            </div>
          ) : (
            <div className="divide-y divide-gray-200">
              {files.map((file) => (
                <div key={file.id} className="p-6 hover:bg-gray-50 transition-colors">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-4">
                      <div className="flex-shrink-0">
                        {getFileIcon(file.type)}
                      </div>
                      <div className="flex-1 min-w-0">
                        <h3 className="text-sm font-medium text-gray-900 truncate">
                          {file.name}
                        </h3>
                        <div className="flex items-center space-x-4 mt-1">
                          <p className="text-sm text-gray-500">{file.size}</p>
                          <p className="text-sm text-gray-500">Uploaded {file.uploadDate}</p>
                          {getStatusBadge(file.status)}
                        </div>
                      </div>
                    </div>
                    
                    <div className="flex items-center space-x-3">
                      <button className="p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100 transition-colors">
                        <Eye className="h-4 w-4" />
                      </button>
                      <button className="p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100 transition-colors">
                        <Download className="h-4 w-4" />
                      </button>
                      <button
                        onClick={() => deleteFile(file.id)}
                        className="p-2 text-gray-400 hover:text-red-600 rounded-lg hover:bg-red-50 transition-colors"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Help Section */}
        <div className="mt-8 bg-blue-50 border border-blue-200 rounded-2xl p-6">
          <div className="flex items-start space-x-3">
            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center flex-shrink-0">
              <span className="text-white font-bold text-sm">V</span>
            </div>
            <div>
              <h3 className="text-lg font-semibold text-blue-900 mb-2">How Knowledge Base Works</h3>
              <div className="text-blue-800 space-y-2">
                <p>• Upload your teaching materials (PDFs, Word documents) to enhance Veron's knowledge</p>
                <p>• Veron will analyze and learn from your content to provide better, more relevant assistance</p>
                <p>• Use the knowledge base to store lesson plans, vocabulary lists, and reference materials</p>
                <p>• All uploaded files are processed securely and used only to improve your teaching experience</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default KnowledgeBase; 