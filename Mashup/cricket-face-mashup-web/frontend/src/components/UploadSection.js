import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, Image, CheckCircle, AlertCircle, Users } from 'lucide-react';
import { toast } from 'react-hot-toast';
import axios from 'axios';

const API_BASE = 'http://localhost:8000';

const UploadSection = ({ onUploadComplete }) => {
  const [uploading, setUploading] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [uploadProgress, setUploadProgress] = useState(0);

  const onDrop = useCallback(async (acceptedFiles) => {
    if (acceptedFiles.length === 0) {
      toast.error('Please select valid image files (JPG, PNG, BMP)');
      return;
    }

    setUploading(true);
    setUploadProgress(0);

    try {
      const formData = new FormData();
      acceptedFiles.forEach(file => {
        formData.append('files', file);
      });

      // Simulate progress
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => Math.min(prev + 10, 90));
      }, 200);

      const response = await axios.post(`${API_BASE}/upload-players`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });

      clearInterval(progressInterval);
      setUploadProgress(100);

      if (response.data.success) {
        setUploadedFiles(response.data.players);
        onUploadComplete(response.data.players);
        toast.success(`Successfully uploaded ${response.data.players.length} players!`);
      } else {
        toast.error('Upload failed. Please try again.');
      }
    } catch (error) {
      console.error('Upload error:', error);
      toast.error('Failed to upload files. Please try again.');
    } finally {
      setUploading(false);
      setTimeout(() => setUploadProgress(0), 1000);
    }
  }, [onUploadComplete]);

  const {
    getRootProps,
    getInputProps,
    isDragActive,
    isDragReject,
    acceptedFiles
  } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.jpg', '.jpeg', '.png', '.bmp']
    },
    multiple: true,
    disabled: uploading
  });

  return (
    <div className="space-y-6">
      {/* Upload Zone */}
      <div className="card p-8">
        <div className="text-center space-y-4">
          <div className="flex items-center justify-center space-x-2">
            <Upload className="h-6 w-6 text-blue-500" />
            <h2 className="text-2xl font-bold text-gray-800">Upload Cricket Players</h2>
          </div>
          <p className="text-gray-600">
            Upload clear front-facing photos of cricket players to start the challenge
          </p>
        </div>

        <div
          {...getRootProps()}
          className={`
            mt-6 p-8 border-2 border-dashed rounded-xl transition-all duration-300 cursor-pointer
            ${isDragActive && !isDragReject ? 'border-blue-400 bg-blue-50' : ''}
            ${isDragReject ? 'border-red-400 bg-red-50' : ''}
            ${!isDragActive ? 'border-gray-300 hover:border-blue-400 hover:bg-blue-50' : ''}
            ${uploading ? 'cursor-not-allowed opacity-50' : ''}
          `}
        >
          <input {...getInputProps()} />
          
          <div className="text-center space-y-4">
            <div className="flex justify-center">
              {uploading ? (
                <div className="w-16 h-16 border-4 border-blue-200 border-t-blue-500 rounded-full animate-spin"></div>
              ) : (
                <div className="p-4 bg-blue-100 rounded-full">
                  <Image className="h-8 w-8 text-blue-500" />
                </div>
              )}
            </div>

            {uploading ? (
              <div className="space-y-2">
                <p className="text-lg font-medium text-blue-600">
                  Processing images... {uploadProgress}%
                </p>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-blue-500 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${uploadProgress}%` }}
                  ></div>
                </div>
              </div>
            ) : (
              <div className="space-y-2">
                <p className="text-lg font-medium text-gray-700">
                  {isDragActive
                    ? isDragReject
                      ? "Some files are not supported"
                      : "Drop the images here"
                    : "Drag & drop cricket player images"
                  }
                </p>
                <p className="text-sm text-gray-500">
                  or <span className="text-blue-500 font-medium">click to browse</span>
                </p>
                <p className="text-xs text-gray-400">
                  Supports JPG, PNG, BMP • Maximum 10MB per file
                </p>
              </div>
            )}
          </div>
        </div>

        {acceptedFiles.length > 0 && !uploading && (
          <div className="mt-4">
            <p className="text-sm text-gray-600 mb-2">Selected files:</p>
            <div className="space-y-1">
              {acceptedFiles.map((file, index) => (
                <div key={index} className="flex items-center space-x-2 text-sm text-gray-700">
                  <CheckCircle className="h-4 w-4 text-green-500" />
                  <span>{file.name}</span>
                  <span className="text-gray-400">({(file.size / 1024 / 1024).toFixed(2)} MB)</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Upload Results */}
      {uploadedFiles.length > 0 && (
        <div className="card p-6">
          <div className="flex items-center space-x-2 mb-4">
            <Users className="h-5 w-5 text-green-500" />
            <h3 className="text-lg font-semibold text-gray-800">
              Uploaded Players ({uploadedFiles.length})
            </h3>
          </div>
          
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {uploadedFiles.map((player, index) => (
              <div key={index} className="space-y-2">
                <div className="aspect-square bg-gray-100 rounded-lg overflow-hidden">
                  <img
                    src={`${API_BASE}${player.image_url}`}
                    alt={player.name}
                    className="w-full h-full object-cover"
                    onError={(e) => {
                      e.target.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgdmlld0JveD0iMCAwIDIwMCAyMDAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxyZWN0IHdpZHRoPSIyMDAiIGhlaWdodD0iMjAwIiBmaWxsPSIjRjNGNEY2Ii8+CjxwYXRoIGQ9Ik0xMDAgNzBDMTA4LjI4NCA3MCA5NS4wODU4IDc3LjE0IDEwOCA4NUMxMDUuNDI5IDkwLjc1IDk0LjU3MTQgOTAuNzUgOTIgODVDOTUuMDg1OCA3Ny4xNCA5MS43MTYgNzAgMTAwIDcwWiIgZmlsbD0iIzlDQTNBRiIvPgo8L3N2Zz4K';
                    }}
                  />
                </div>
                <div className="text-center">
                  <p className="text-sm font-medium text-gray-800 truncate">
                    {player.name}
                  </p>
                  <div className="flex items-center justify-center space-x-1 mt-1">
                    {player.face_detected ? (
                      <>
                        <CheckCircle className="h-3 w-3 text-green-500" />
                        <span className="text-xs text-green-600">Face detected</span>
                      </>
                    ) : (
                      <>
                        <AlertCircle className="h-3 w-3 text-yellow-500" />
                        <span className="text-xs text-yellow-600">No face detected</span>
                      </>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
          
          <div className="mt-4 p-3 bg-green-50 rounded-lg border border-green-200">
            <div className="flex items-center space-x-2">
              <CheckCircle className="h-4 w-4 text-green-500" />
              <p className="text-sm text-green-700">
                Players uploaded successfully! You can now start the game.
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default UploadSection;