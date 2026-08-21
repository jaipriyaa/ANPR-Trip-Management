import api from './client';

export const uploadMedia = (file, options = {}, onProgress) => {
  const formData = new FormData();
  formData.append('file', file);
  const gateId = options.gate_id || options.gateId;
  const driverId = options.driver_id || options.driverId;
  const driverName = options.driver_name || options.driverName;
  const transporterId = options.transporter_id || options.transporterId;

  if (gateId) formData.append('gate_id', gateId);
  if (driverId) formData.append('driver_id', driverId);
  if (driverName) formData.append('driver_name', driverName);
  if (transporterId) formData.append('transporter_id', transporterId);
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

export const getDetectionHistory = (vehicleId, params) => {
  if (!vehicleId || typeof vehicleId === 'object') {
    return api.get('/vehicle-recognition/detections', { params: vehicleId || params });
  }
  return api.get(`/vehicle-recognition/vehicles/${vehicleId}/detections`, { params });
};

export const getAllDetections = (params) =>
  api.get('/vehicle-recognition/detections', { params });

export const getDetectionDetail = (detectionId) =>
  api.get(`/vehicle-recognition/detections/${detectionId}`);

export const searchByPlate = (plate) =>
  api.get('/vehicle-recognition/search', { params: { plate } });

export const getMediaUrl = (fileType, filename) =>
  `/api/v1/vehicle-recognition/media/${fileType}/${filename}`;
