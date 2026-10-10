
import { useEffect, useMemo, useState } from 'react'
import {
  ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, PieChart, Pie, Cell, Legend, AreaChart, Area,
} from 'recharts'
import './App.css'

const API = 'http://127.0.0.1:8000'
const COLORS = ['#36e5ae', '#8b7cff', '#ffbf69', '#ff718b', '#62b6ff']
const normalize = value => String(value ?? '').trim().toLowerCase()

function App() {
  const [tickets, setTickets] = useState([])
  const [ticketText, setTicketText] = useState('')
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState('All')
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')

  async function loadTickets() {
    try {
      const response = await fetch(`${API}/tickets`)
      if (!response.ok) throw new Error('Could not load tickets')
      const data = await response.json()
      setTickets(Array.isArray(data) ? data : data.tickets ?? [])
      setError('')
    } catch {
      setError('Backend connection failed. Start the FastAPI server and refresh.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { loadTickets() }, [])

  const stats = useMemo(() => ({
    total: tickets.length,
    open: tickets.filter(t => normalize(t.status) === 'open').length,
    resolved: tickets.filter(t => normalize(t.status) === 'resolved').length,
    high: tickets.filter(t => normalize(t.priority) === 'high').length,
    progress: tickets.length
      ? Math.round(tickets.filter(t => normalize(t.status) === 'resolved').length / tickets.length * 100)
      : 0,
  }), [tickets])

  const categoryData = useMemo(() => {
    const counts = {}
    tickets.forEach(t => {
      const category = t.category || 'Uncategorized'
      counts[category] = (counts[category] || 0) + 1
    })
    return Object.entries(counts)
      .map(([name, count]) => ({ name, count }))
      .sort((a, b) => b.count - a.count)
  }, [tickets])

  const priorityData = useMemo(() => {
    const options = [
      { name: 'High', color: '#ff718b' },
      { name: 'Medium', color: '#ffbf69' },
      { name: 'Low', color: '#36e5ae' },
    ]
    return options.map(item => ({
      ...item,
      value: tickets.filter(t => normalize(t.priority) === item.name.toLowerCase()).length,
    }))
  }, [tickets])

  const statusData = useMemo(() => [
    { name: 'Open', count: stats.open, fill: '#ffbf69' },
    {
      name: 'In Progress',
      count: tickets.filter(t => normalize(t.status) === 'in progress').length,
      fill: '#8b7cff',
    },
    { name: 'Resolved', count: stats.resolved, fill: '#36e5ae' },
  ], [tickets, stats])

  const trendData = useMemo(() => {
    const days = {}
    tickets.forEach(t => {
      const raw = t.created_at
      const date = raw ? new Date(raw) : null
      const key = date && !Number.isNaN(date.getTime())
        ? date.toLocaleDateString('en-IN', { day: '2-digit', month: 'short' })
        : 'Date unknown'
      days[key] = (days[key] || 0) + 1
    })
    return Object.entries(days).map(([date, count]) => ({ date, count })).slice(-7)
  }, [tickets])

  const filteredTickets = useMemo(() => {
    return [...tickets].reverse().filter(t => {
      const query = normalize(search)
      const matchesSearch = [
        t.id, t.ticket, t.text, t.description, t.category, t.priority, t.status,
      ].some(value => normalize(value).includes(query))
      const matchesStatus = statusFilter === 'All' || normalize(t.status) === normalize(statusFilter)
      return matchesSearch && matchesStatus
    })
  }, [tickets, search, statusFilter])

  async function submitTicket(event) {
    event.preventDefault()
    if (!ticketText.trim()) return

    setSubmitting(true)
    setMessage('')
    setError('')

    try {
      const response = await fetch(`${API}/tickets`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ticket: ticketText.trim(), text: ticketText.trim() }),
      })
      if (!response.ok) throw new Error(await response.text())
      setTicketText('')
      setMessage('Ticket submitted successfully.')
      await loadTickets()
    } catch (err) {
      setError(`Submission failed: ${err.message}`)
    } finally {
      setSubmitting(false)
    }
  }

  async function updateStatus(ticketId, status) {
    setMessage('')
    setError('')
    try {
      const response = await fetch(`${API}/tickets/${ticketId}/status`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status }),
      })
      if (!response.ok) throw new Error(await response.text())
      setMessage(`Ticket #${ticketId} updated.`)
      await loadTickets()
    } catch (err) {
      setError(`Status update failed: ${err.message}`)
    }
  }

  return (
    <main className="app-shell">
      <aside className="sidebar">
        <div className="side-brand">
          <div className="logo-mark">S<span>+</span></div>
          <div><strong>Support<span className="green-text">Copilot</span></strong><small>AI OPERATIONS</small></div>
        </div>
        <div className="nav-caption">WORKSPACE</div>
        <a className="nav-link active" href="#overview"><span>◈</span> Overview</a>
        <a className="nav-link" href="#analytics"><span>▥</span> Analytics</a>
        <a className="nav-link" href="#evaluation"><span>✳</span> AI Evaluation</a>
        <a className="nav-link" href="#tickets"><span>▤</span> Ticket Database</a>
        <div className="sidebar-bottom">
          <div className="connection"><span className="pulse-dot" /> API CONNECTION <strong>LOCAL</strong></div>
          <p>Student Support Copilot</p>
          <small>React · FastAPI · SQLite</small>
        </div>
      </aside>

      <div className="main-content">
        <header className="topbar">
          <div className="breadcrumb">Workspace <span>/</span> <strong>Overview</strong></div>
          <div className="top-actions">
            <span className="system-status"><i /> System dashboard</span>
            <button className="icon-button" onClick={loadTickets} title="Refresh database">↻</button>
          </div>
        </header>

        <section id="overview" className="page-intro">
          <div>
            <div className="overline"><span className="sparkle">✳</span> INTELLIGENT STUDENT SUPPORT</div>
            <h1>Support <span className="gradient-text">Overview</span></h1>
            <p>One workspace for ticket intelligence, service performance and AI evaluation.</p>
          </div>
          <a href="#create-ticket" className="new-ticket-button">＋ New ticket</a>
        </section>

        {error && <div className="alert alert-error">{error}</div>}
        {message && <div className="alert alert-success">✓ {message}</div>}

        <section className="metrics-grid">
          <MetricCard label="TOTAL TICKETS" value={stats.total} symbol="▤" accent="mint" note="All database records" />
          <MetricCard label="OPEN TICKETS" value={stats.open} symbol="◷" accent="amber" note="Awaiting resolution" />
          <MetricCard label="RESOLVED" value={stats.resolved} symbol="✓" accent="violet" note={`${stats.progress}% of all tickets`} />
          <MetricCard label="HIGH PRIORITY" value={stats.high} symbol="↗" accent="rose" note="Needs attention" />
        </section>

        <section id="analytics" className="section-block">
          <div className="section-title">
            <div><span className="section-kicker">LIVE INSIGHTS</span><h2>Analytics <span className="subtle-title">/ Ticket intelligence</span></h2></div>
            <span className="data-chip"><i /> Based on database records</span>
          </div>

          <div className="chart-grid">
            <article className="glass-panel chart-panel category-panel">
              <PanelTitle title="Ticket categories" subtitle="Volume by support topic" tag="VOLUME" />
              <div className="chart-area">
                {categoryData.length ? (
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={categoryData} margin={{ top: 12, right: 8, left: -18, bottom: 38 }}>
                      <CartesianGrid stroke="#243148" strokeDasharray="3 5" vertical={false} />
                      <XAxis dataKey="name" interval={0} angle={-18} textAnchor="end" tick={{ fill: '#91a2ba', fontSize: 10 }} axisLine={false} tickLine={false} />
                      <YAxis allowDecimals={false} tick={{ fill: '#91a2ba', fontSize: 10 }} axisLine={false} tickLine={false} />
                      <Tooltip contentStyle={tooltipStyle} cursor={{ fill: '#1d2a3b' }} />
                      <Bar dataKey="count" name="Tickets" fill="#36e5ae" radius={[6, 6, 0, 0]} maxBarSize={48} />
                    </BarChart>
                  </ResponsiveContainer>
                ) : <EmptyState loading={loading} />}
              </div>
            </article>

            <article className="glass-panel chart-panel trend-panel">
              <PanelTitle title="Ticket activity" subtitle="Created ticket trend" tag="ACTIVITY" />
              <div className="chart-area">
                {trendData.length ? (
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={trendData} margin={{ top: 12, right: 8, left: -18, bottom: 8 }}>
                      <defs>
                        <linearGradient id="ticketGradient" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="0%" stopColor="#8b7cff" stopOpacity={0.45} />
                          <stop offset="100%" stopColor="#8b7cff" stopOpacity={0.02} />
                        </linearGradient>
                      </defs>
                      <CartesianGrid stroke="#243148" strokeDasharray="3 5" vertical={false} />
                      <XAxis dataKey="date" tick={{ fill: '#91a2ba', fontSize: 10 }} axisLine={false} tickLine={false} />
                      <YAxis allowDecimals={false} tick={{ fill: '#91a2ba', fontSize: 10 }} axisLine={false} tickLine={false} />
                      <Tooltip contentStyle={tooltipStyle} />
                      <Area type="monotone" dataKey="count" name="Created tickets" stroke="#9a8cff" strokeWidth={3} fill="url(#ticketGradient)" activeDot={{ r: 6, fill: '#36e5ae' }} />
                    </AreaChart>
                  </ResponsiveContainer>
                ) : <EmptyState loading={loading} />}
              </div>
            </article>

            <article className="glass-panel chart-panel priority-panel">
              <PanelTitle title="Priority mix" subtitle="Urgency across all tickets" tag="URGENCY" />
              <div className="chart-area donut-area">
                {tickets.length ? (
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie data={priorityData} dataKey="value" nameKey="name" cx="50%" cy="46%" innerRadius={58} outerRadius={88} paddingAngle={5} stroke="none">
                        {priorityData.map(item => <Cell key={item.name} fill={item.color} />)}
                      </Pie>
                      <Tooltip contentStyle={tooltipStyle} />
                      <Legend verticalAlign="bottom" iconType="circle" formatter={value => <span className="legend-text">{value}</span>} />
                      <text x="50%" y="43%" textAnchor="middle" dominantBaseline="middle" fill="#f0f5ff" fontSize="25" fontWeight="700">{stats.total}</text>
                      <text x="50%" y="54%" textAnchor="middle" fill="#8799b2" fontSize="10">TOTAL</text>
                    </PieChart>
                  </ResponsiveContainer>
                ) : <EmptyState loading={loading} />}
              </div>
            </article>

            <article className="glass-panel chart-panel status-chart-panel">
              <PanelTitle title="Resolution status" subtitle="Current ticket lifecycle" tag="WORKFLOW" />
              <div className="chart-area">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={statusData} layout="vertical" margin={{ top: 12, right: 12, left: 14, bottom: 8 }}>
                    <CartesianGrid stroke="#243148" strokeDasharray="3 5" horizontal={false} />
                    <XAxis type="number" allowDecimals={false} tick={{ fill: '#91a2ba', fontSize: 10 }} axisLine={false} tickLine={false} />
                    <YAxis type="category" dataKey="name" width={82} tick={{ fill: '#c4d0e0', fontSize: 11 }} axisLine={false} tickLine={false} />
                    <Tooltip contentStyle={tooltipStyle} />
                    <Bar dataKey="count" name="Tickets" radius={[0, 7, 7, 0]} maxBarSize={28}>
                      {statusData.map(item => <Cell key={item.name} fill={item.fill} />)}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </article>
          </div>
        </section>

        <section id="evaluation" className="section-block evaluation-section">
          <div className="section-title">
            <div><span className="section-kicker">MODEL QUALITY</span><h2>AI Evaluation <span className="subtle-title">/ Test results</span></h2></div>
            <span className="evaluation-badge"><span /> TEST SET PASSED</span>
          </div>
          <div className="evaluation-grid">
            <article className="evaluation-hero glass-panel">
              <div className="evaluation-orbit"><span>✳</span></div>
              <div className="eval-copy">
                <span className="section-kicker">LABELED TEST CASES</span>
                <div className="eval-score">36<span>/36</span></div>
                <h3>Test cases passed</h3>
                <p>All 36 cases in the existing labeled evaluation set passed.</p>
                <div className="eval-progress"><span /></div>
                <div className="eval-foot"><span>Observed pass rate</span><strong>100% on this test set</strong></div>
              </div>
            </article>
            <article className="glass-panel evaluation-details">
              <PanelTitle title="Evaluation summary" subtitle="What has been tested" tag="VALIDATION" />
              <div className="eval-detail-row"><span className="detail-icon mint">✓</span><div><strong>Rule-based classification</strong><p>36 of 36 labeled cases passed</p></div><span className="result-pill">PASS</span></div>
              <div className="eval-detail-row"><span className="detail-icon violet">✳</span><div><strong>Gemini-assisted triage</strong><p>Uses the configured LLM when available</p></div><span className="result-pill neutral">CHECK LIVE</span></div>
              <div className="eval-detail-row"><span className="detail-icon amber">↻</span><div><strong>Fallback handling</strong><p>Rule-based path available when the LLM fails</p></div><span className="result-pill neutral">VERIFY</span></div>
              <p className="evaluation-note">The 100% result applies only to the existing 36-case test set. It is not a claim of 100% accuracy on all real-world tickets. Live LLM quality and fallback behavior should be tested separately.</p>
            </article>
          </div>
        </section>

        <section id="create-ticket" className="section-block">
          <div className="section-title">
            <div><span className="section-kicker">SUPPORT WORKSPACE</span><h2>Ticket management <span className="subtle-title">/ Create & resolve</span></h2></div>
          </div>
          <div className="management-grid">
            <article className="glass-panel create-panel">
              <PanelTitle title="Create a ticket" subtitle="Send a student issue for triage" tag="NEW" />
              <form onSubmit={submitTicket}>
                <label htmlFor="ticketText">STUDENT ISSUE</label>
                <textarea id="ticketText" value={ticketText} onChange={e => setTicketText(e.target.value)} placeholder="Example: I paid for my course, but my batch is not visible." rows="4" required />
                <div className="form-hint"><span>✳</span> Describe the issue clearly for better classification.</div>
                <button className="submit-button" type="submit" disabled={submitting}>{submitting ? 'Analyzing ticket…' : '✳  Submit for triage'}</button>
              </form>
            </article>
            <article className="glass-panel quick-summary">
              <PanelTitle title="Service snapshot" subtitle="Current workload overview" tag="LIVE" />
              <div className="snapshot-number">{stats.progress}<span>%</span></div>
              <p className="snapshot-caption">of recorded tickets are resolved</p>
              <div className="snapshot-track"><span style={{ width: `${stats.progress}%` }} /></div>
              <div className="snapshot-stats">
                <div><span className="mini-dot amber-dot" /><span>Open</span><strong>{stats.open}</strong></div>
                <div><span className="mini-dot mint-dot" /><span>Resolved</span><strong>{stats.resolved}</strong></div>
                <div><span className="mini-dot rose-dot" /><span>High priority</span><strong>{stats.high}</strong></div>
              </div>
            </article>
          </div>
        </section>

        <section id="tickets" className="section-block database-section">
          <div className="section-title">
            <div><span className="section-kicker">SQLITE RECORDS</span><h2>Ticket database <span className="subtle-title">/ Live records</span></h2></div>
            <span className="record-count">{tickets.length} RECORDS</span>
          </div>
          <article className="glass-panel database-panel">
            <div className="database-toolbar">
              <div className="search-box"><span>⌕</span><input value={search} onChange={e => setSearch(e.target.value)} placeholder="Search issue, category, priority…" /></div>
              <select value={statusFilter} onChange={e => setStatusFilter(e.target.value)} aria-label="Filter by status">
                <option>All</option><option>Open</option><option>In Progress</option><option>Resolved</option>
              </select>
              <button className="secondary-button" onClick={loadTickets}>↻ Refresh</button>
            </div>
            {loading ? <EmptyState loading /> : filteredTickets.length === 0 ? (
              <div className="database-empty"><span>▤</span><strong>No matching tickets</strong><p>Submit a new ticket or adjust your search.</p></div>
            ) : (
              <div className="table-scroll">
                <table className="ticket-table">
                  <thead><tr><th>ID</th><th>STUDENT ISSUE</th><th>CATEGORY</th><th>PRIORITY</th><th>STATUS</th><th>UPDATE STATUS</th></tr></thead>
                  <tbody>
                    {filteredTickets.map((t, i) => (
                      <tr key={t.id ?? i}>
                        <td><span className="ticket-id">#{t.id ?? '—'}</span></td>
                        <td className="issue-cell">{t.ticket ?? t.text ?? t.description ?? '—'}</td>
                        <td><span className="category-label">{t.category ?? 'Unclassified'}</span></td>
                        <td><span className={`priority-tag ${normalize(t.priority)}`}>{t.priority ?? '—'}</span></td>
                        <td><span className={`status-tag ${normalize(t.status).replace(/\s/g, '-')}`}>{t.status ?? 'Open'}</span></td>
                        <td><select aria-label={`Update ticket ${t.id}`} value={t.status ?? 'Open'} disabled={t.id == null} onChange={e => updateStatus(t.id, e.target.value)}><option>Open</option><option>In Progress</option><option>Resolved</option></select></td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
            <div className="database-footer"><span>Showing {filteredTickets.length} of {tickets.length} records</span><span><i className="pulse-dot" /> Connected to local API</span></div>
          </article>
        </section>

        <footer className="app-footer"><span>✳ Student Support Copilot</span><span>AI-assisted triage · React · FastAPI · SQLite</span></footer>
      </div>
    </main>
  )
}

const tooltipStyle = {
  background: '#101a2a',
  border: '1px solid #34445b',
  borderRadius: '10px',
  color: '#edf4ff',
  fontSize: '12px',
}

function MetricCard({ label, value, symbol, accent, note }) {
  return (
    <article className={`metric-card ${accent}`}>
      <div className="metric-top"><span>{label}</span><span className="metric-symbol">{symbol}</span></div>
      <div className="metric-value">{value}</div>
      <div className="metric-note"><span className="metric-note-dot" />{note}</div>
      <div className="metric-shine" />
    </article>
  )
}

function PanelTitle({ title, subtitle, tag }) {
  return (
    <div className="panel-title">
      <div><h3>{title}</h3><p>{subtitle}</p></div>
      <span className="panel-tag">{tag}</span>
    </div>
  )
}

function EmptyState({ loading }) {
  return <div className="chart-empty">{loading ? 'Loading data…' : 'No data yet. Submit a ticket to populate analytics.'}</div>
}

export default App