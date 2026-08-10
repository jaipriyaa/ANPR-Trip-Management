import api from './client';

export const uploadMedia = (file, options = {}, onProgress) => {
  const formData = new FormData();
  formData.append('file', file);
  if (options.gate_id) formData.append('gate_id', options.gate_id);
  if (options.driver_id) formData.append('driver_id', options.driver_id);
  if (options.driver_name) formData.append('driver_name', options.driver_name);
  if (options.transporter_id) formData.append('transporter_id', options.transporter_id);
  if (options.direction) formData.append('direction', options.direction);
  if (options.purpose) formData.append('purpose', options.purpose);
  if (options.destination) formData.append('destination', options.destination);

  return api.post('/vehicle-recognition/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 300000,
    onUploadProgress: onProgress,
  });
};

export const syncDatasetDetection = (detectionId, payload) =>
  api.post(`/vehicle-recognition/detections/${detectionId}/sync`, payload);


export const getRecognizedVehicles = (params) =>
  api.get('/vehicle-recognition/vehicles', { params });

export const getRecognizedVehicle = (id) =>
  api.get(`/vehicle-recognition/vehicles/${id}`);

export const getDetectionHistory = (vehicleId, params) =>
  api.get(`/vehicle-recognition/vehicles/${vehicleId}/detections`, { params });

export const getAllDetections = (params) =>
  api.get('/vehicle-recognition/detections', { params });

export const getDetectionDetail = (detectionId) =>
  api.get(`/vehicle-recognition/detections/${detectionId}`);

export const searchByPlate = (plate) =>
  api.get('/vehicle-recognition/search', { params: { plate } });

export const getMediaUrl = (fileType, filename) =>
  `/api/v1/vehicle-recognition/media/${fileType}/${filename}`;
