import axios from "axios";

const api = axios.create({
  baseURL: process.env.REACT_APP_API_BASE_URL || "http://localhost:8000",
});

export const fetchCampaigns = async () => {
  const response = await api.get("/campaigns/");
  return response.data;
};

export const createCampaign = async (payload) => {
  const response = await api.post("/campaigns/", payload);
  return response.data;
};

export const pledgeCampaign = async (campaignId, payload) => {
  const response = await api.post(`/campaigns/${campaignId}/pledge`, payload);
  return response.data;
};

export default api;
