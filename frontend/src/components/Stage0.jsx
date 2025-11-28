import { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import './Stage0.css';

export default function Stage0({ researchFindings }) {
  const [activeTab, setActiveTab] = useState(0);

  if (!researchFindings || researchFindings.length === 0) {
    return null;
  }

  const formatCategoryName = (category) => {
    return category
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  return (
    <div className="stage stage0">
      <h3 className="stage-title">Stage 0: Research Preprocessing</h3>
      <p className="stage-description">
        Specialized research gathered before council deliberation
      </p>

      <div className="tabs">
        {researchFindings.map((finding, index) => (
          <button
            key={index}
            className={`tab ${activeTab === index ? 'active' : ''}`}
            onClick={() => setActiveTab(index)}
          >
            {formatCategoryName(finding.category)}
          </button>
        ))}
      </div>

      <div className="tab-content">
        <div className="research-category">{formatCategoryName(researchFindings[activeTab].category)}</div>
        <div className="research-findings markdown-content">
          <ReactMarkdown>{researchFindings[activeTab].findings}</ReactMarkdown>
        </div>
      </div>
    </div>
  );
}
