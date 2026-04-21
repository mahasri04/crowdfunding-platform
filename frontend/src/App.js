import React, { useEffect, useMemo, useState } from "react";

import { createCampaign, fetchCampaigns, pledgeCampaign } from "./api";
import "./App.css";

const initialCampaign = { title: "", goal: "", deadline: "" };
const initialPledge = { campaignId: "", user_name: "", amount: "" };

function App() {
  const [campaignForm, setCampaignForm] = useState(initialCampaign);
  const [pledgeForm, setPledgeForm] = useState(initialPledge);
  const [campaigns, setCampaigns] = useState([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [lastUpdated, setLastUpdated] = useState("");

  const loadCampaigns = async () => {
    setLoading(true);
    setError("");
    try {
      const data = await fetchCampaigns();
      setCampaigns(data);
      setLastUpdated(new Date().toLocaleTimeString());
    } catch (err) {
      setError(err?.response?.data?.detail || "Failed to load campaigns");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadCampaigns();
    const intervalId = setInterval(loadCampaigns, 5000);
    return () => clearInterval(intervalId);
  }, []);

  const onCreateCampaign = async (e) => {
    e.preventDefault();
    setError("");
    try {
      await createCampaign({
        title: campaignForm.title,
        goal: Number(campaignForm.goal),
        deadline: new Date(campaignForm.deadline).toISOString(),
      });
      setCampaignForm(initialCampaign);
      await loadCampaigns();
    } catch (err) {
      setError(err?.response?.data?.detail || "Campaign creation failed");
    }
  };

  const onPledge = async (e) => {
    e.preventDefault();
    setError("");
    try {
      await pledgeCampaign(Number(pledgeForm.campaignId), {
        user_name: pledgeForm.user_name,
        amount: Number(pledgeForm.amount),
      });
      setPledgeForm(initialPledge);
      await loadCampaigns();
    } catch (err) {
      setError(err?.response?.data?.detail || "Pledge failed");
    }
  };

  const campaignOptions = useMemo(
    () =>
      campaigns.map((c) => (
        <option key={c.id} value={c.id}>
          {c.title} (#{c.id})
        </option>
      )),
    [campaigns]
  );

  return (
    <main className="app-shell">
      <header className="app-header">
        <h1>Crowdfunding Platform</h1>
        <p>
          Real-time refresh every 5 seconds{lastUpdated ? ` (last updated: ${lastUpdated})` : ""}.
        </p>
      </header>

      {error ? <p className="error-banner">{error}</p> : null}

      <section className="panel">
        <h2>Create Campaign</h2>
        <form onSubmit={onCreateCampaign} className="form-grid">
          <input
            placeholder="Title"
            value={campaignForm.title}
            onChange={(e) => setCampaignForm((s) => ({ ...s, title: e.target.value }))}
            required
          />
          <input
            placeholder="Goal"
            type="number"
            step="0.01"
            value={campaignForm.goal}
            onChange={(e) => setCampaignForm((s) => ({ ...s, goal: e.target.value }))}
            required
          />
          <input
            type="datetime-local"
            value={campaignForm.deadline}
            onChange={(e) => setCampaignForm((s) => ({ ...s, deadline: e.target.value }))}
            required
          />
          <button type="submit" className="btn-primary">Create</button>
        </form>
      </section>

      <section className="panel">
        <h2>Pledge to Campaign</h2>
        <form onSubmit={onPledge} className="form-grid">
          <select
            value={pledgeForm.campaignId}
            onChange={(e) => setPledgeForm((s) => ({ ...s, campaignId: e.target.value }))}
            required
          >
            <option value="">Select campaign</option>
            {campaignOptions}
          </select>
          <input
            placeholder="User Name"
            value={pledgeForm.user_name}
            onChange={(e) => setPledgeForm((s) => ({ ...s, user_name: e.target.value }))}
            required
          />
          <input
            placeholder="Amount"
            type="number"
            step="0.01"
            value={pledgeForm.amount}
            onChange={(e) => setPledgeForm((s) => ({ ...s, amount: e.target.value }))}
            required
          />
          <button type="submit" className="btn-primary">Pledge</button>
        </form>
      </section>

      <section className="panel">
        <h2>Campaign Progress</h2>
        {loading ? <p className="meta">Loading...</p> : null}
        {campaigns.map((c) => {
          const progress = c.goal === 0 ? 0 : Math.round((c.pledged / c.goal) * 100);
          return (
            <article key={c.id} className="campaign-card">
              <h3>{c.title}</h3>
              <p className="meta">
                Goal: ${c.goal.toFixed(2)} | Pledged: ${c.pledged.toFixed(2)}
              </p>
              <p className="status">Status: {c.status}</p>
              <progress value={c.pledged} max={c.goal} className="native-progress" />
              <p className="meta">{progress}% funded</p>
            </article>
          );
        })}
      </section>

      <section className="panel">
        <h2>Funding Chart (Bonus)</h2>
        {campaigns.map((c) => {
          const percent = c.goal === 0 ? 0 : Math.min(100, Math.round((c.pledged / c.goal) * 100));
          return (
            <div key={`chart-${c.id}`} className="chart-row">
              <div className="chart-labels">
                <span>{c.title}</span>
                <span>{percent}%</span>
              </div>
              <div className="chart-track">
                <div
                  className="chart-fill"
                  style={{
                    width: `${percent}%`,
                    background: percent >= 100 ? "#16a34a" : "#2563eb"
                  }}
                />
              </div>
            </div>
          );
        })}
      </section>
    </main>
  );
}

export default App;
