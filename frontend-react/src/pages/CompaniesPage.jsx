import { useApi } from '../hooks/useApi';
import Layout from '../components/Layout';
import Card from '../components/ui/Card';
import { ExternalLink, Building2, CheckSquare } from 'lucide-react';
import './companies.css';

function CompaniesPage() {
  const { data, loading } = useApi('/companies/');

  if (loading) return <Layout title="Companies"><div className="skeleton skeleton--card" /></Layout>;
  if (!data) return null;

  const { summary, companies, checklist } = data;

  return (
    <Layout title="Companies" subtitle={`${summary.target_count} targets - ${summary.average_readiness}% avg readiness`}>
      <div className="companies">
        <div className="grid grid--3">
          <div className="stat-card">
            <div className="stat-card__label">Target companies</div>
            <div className="stat-card__value">{summary.target_count}</div>
          </div>
          <div className="stat-card">
            <div className="stat-card__label">Avg readiness</div>
            <div className="stat-card__value">{summary.average_readiness}%</div>
          </div>
          <div className="stat-card">
            <div className="stat-card__label">With career portals</div>
            <div className="stat-card__value">{summary.source_count}</div>
          </div>
        </div>

        <Card>
          <Card.Header><span className="companies__section-title"><CheckSquare size={18} />Application checklist</span></Card.Header>
          <Card.Body>
            <div className="companies__checklist">
              {checklist.map((item, i) => (
                <div key={i} className="companies__checklist-item">
                  <div className="companies__checkbox" />
                  <span>{item}</span>
                </div>
              ))}
            </div>
          </Card.Body>
        </Card>

        <div className="companies__list">
          {companies.map((c) => (
            <Card key={c.name} hover className="companies__card">
              <div className="companies__card-header">
                <div className="companies__card-title">
                  <div className="companies__card-icon">
                    <Building2 size={20} />
                  </div>
                  <div>
                    <h3>{c.full_name}</h3>
                    <span>{c.focus}</span>
                  </div>
                </div>
                <span className={`badge badge--${c.tone}`}>{c.readiness}% ready</span>
              </div>

              {c.roles.length > 0 && (
                <div className="companies__role-list">
                  <span>Roles:</span>
                  {c.roles.map((role) => (
                    <span key={role} className="companies__role-tag">{role}</span>
                  ))}
                </div>
              )}

              {c.eligibility_notes && c.eligibility_notes.length > 0 && (
                <div className="companies__eligibility">
                  <span>Eligibility:</span>
                  <ul className="companies__notes">
                    {c.eligibility_notes.map((note) => (
                      <li key={note}>{note}</li>
                    ))}
                  </ul>
                </div>
              )}

              {c.official_url && (
                <a href={c.official_url} target="_blank" rel="noopener noreferrer" className="companies__link">
                  <ExternalLink size={14} />
                  <span>Visit career portal</span>
                </a>
              )}
            </Card>
          ))}
        </div>
      </div>
    </Layout>
  );
}

export default CompaniesPage;
