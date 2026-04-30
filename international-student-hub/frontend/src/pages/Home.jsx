import { Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import './Home.css'

const FEATURES = [
  {
    icon: '✅',
    title: 'Arrival Checklist',
    desc: 'Step-by-step tasks for your first weeks — ARC, SIM, bank account, health insurance.',
    link: '/checklist',
    linkText: 'View checklist',
  },
  {
    icon: '🗺️',
    title: 'Service Directory',
    desc: 'Find student-friendly restaurants, clinics, banks, and SIM shops near your campus.',
    link: '/directory',
    linkText: 'Browse services',
  },
  {
    icon: '💬',
    title: 'Community Q&A',
    desc: 'Ask questions, share tips, and connect with other international students in Taiwan.',
    link: '/community',
    linkText: 'Join discussion',
  },
  {
    icon: '🤖',
    title: 'LINE Bot',
    desc: 'Add our LINE Bot for instant answers to your most common questions, anytime.',
    link: '#line-bot',
    linkText: 'Coming soon',
  },
]

const UNIVERSITIES = ['NSYSU', 'NTU', 'NCKU', 'NTHU', 'NYCU', 'NCU', 'NTNU', 'FJU']

export default function Home() {
  const { user } = useAuth()

  return (
    <div className="home page">
      {/* ── Hero ─────────────────────────────────────────────── */}
      <section className="hero">
        <div className="hero__bg-dots" aria-hidden="true" />
        <div className="container">
          <div className="hero__content fade-up">
            <div className="hero__eyebrow">
              <span className="badge badge-red">🇹🇼 Taiwan</span>
              <span className="badge badge-navy">For International Students</span>
            </div>
            <h1 className="hero__title">
              Your first weeks<br />
              <em>made easy.</em>
            </h1>
            <p className="hero__sub">
              Everything you need to navigate arriving in Taiwan — checklists, services,
              community knowledge, and real-time help. All in one place.
            </p>
            <div className="hero__actions">
              {user ? (
                <Link to="/checklist" className="btn btn-primary hero__cta">
                  Continue my checklist →
                </Link>
              ) : (
                <>
                  <Link to="/register" className="btn btn-primary hero__cta">
                    Get started free →
                  </Link>
                  <Link to="/directory" className="btn btn-outline">
                    Browse services
                  </Link>
                </>
              )}
            </div>
          </div>

          {/* University tags */}
          <div className="hero__unis fade-up fade-up-2">
            <span className="hero__unis-label">Serving students at</span>
            <div className="hero__unis-list">
              {UNIVERSITIES.map(u => (
                <span key={u} className="hero__uni-tag">{u}</span>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* ── Features ─────────────────────────────────────────── */}
      <section className="features">
        <div className="container">
          <div className="section-header fade-up">
            <h2>Everything you need</h2>
            <p>Built by international students, for international students.</p>
          </div>
          <div className="features__grid">
            {FEATURES.map((f, i) => (
              <Link
                key={f.title}
                to={f.link}
                className={`feature-card card fade-up fade-up-${i + 1}`}
              >
                <div className="feature-card__icon">{f.icon}</div>
                <h3 className="feature-card__title">{f.title}</h3>
                <p className="feature-card__desc">{f.desc}</p>
                <span className="feature-card__link">{f.linkText} →</span>
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* ── CTA strip ────────────────────────────────────────── */}
      {!user && (
        <section className="home-cta">
          <div className="container">
            <div className="home-cta__inner fade-up">
              <div>
                <h2>Ready to get started?</h2>
                <p>Join hundreds of international students already using ISH Taiwan.</p>
              </div>
              <Link to="/register" className="btn btn-primary">
                Create free account →
              </Link>
            </div>
          </div>
        </section>
      )}

      {/* ── Footer ───────────────────────────────────────────── */}
      <footer className="home-footer">
        <div className="container">
          <span className="navbar__logo-mark">ISH</span>
          <p>© 2026 International Student Hub — Taiwan · Built at NSYSU</p>
        </div>
      </footer>
    </div>
  )
}
