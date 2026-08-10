import api from './client';

// Transporters API
export const getTransporters = (params) => api.get('/transporters', { params });
export const getTransporter = (id) => api.get(`/transporters/${id}`);
export const createTransporter = (data) => api.post('/transporters', data);
export const updateTransporter = (id, data) => api.put(`/transporters/${id}`, data);
export const deleteTransporter = (id) => api.delete(`/transporters/${id}`);

// Vehicles API
export const getVehicles = (params) => api.get('/vehicles', { params });
export const getVehicle = (id) => api.get(`/vehicles/${id}`);
export const createVehicle = (data) => api.post('/vehicles', data);
export const updateVehicle = (id, data) => api.put(`/vehicles/${id}`, data);
export const deleteVehicle = (id) => api.delete(`/vehicles/${id}`);

// Vehicle Plates API
export const getVehiclePlates = (params) => api.get('/vehicle-plates', { params });
export const createVehiclePlate = (data) => api.post('/vehicle-plates', data);
export const deleteVehiclePlate = (id) => api.delete(`/vehicle-plates/${id}`);

// Drivers API
export const getDrivers = (params) => api.get('/drivers', { params });
export const getDriver = (id) => api.get(`/drivers/${id}`);
export const createDriver = (data) => api.post('/drivers', data);
export const updateDriver = (id, data) => api.put(`/drivers/${id}`, data);
export const deleteDriver = (id) => api.delete(`/drivers/${id}`);

// Gates API
export const getGates = (params) => api.get('/gates', { params });

