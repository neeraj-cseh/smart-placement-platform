import React, { useEffect, useRef } from 'react';
import mermaid from 'mermaid';

const Mermaid = ({ chart }) => {
  const ref = useRef(null);

  useEffect(() => {
    mermaid.initialize({
      startOnLoad: false,
      theme: 'dark',
      securityLevel: 'loose',
    });

    if (ref.current && chart) {
        // Strip markdown code block backticks if present
        const cleanChart = chart.replace(/^```mermaid\n/, '').replace(/\n```$/, '');
        mermaid.render(`mermaid-${Math.random().toString(36).substr(2, 9)}`, cleanChart).then(({ svg }) => {
            if (ref.current) {
            ref.current.innerHTML = svg;
            }
        }).catch(e => {
            console.error("Mermaid parsing failed", e);
        });
    }
  }, [chart]);

  return <div ref={ref} className="mermaid-chart" style={{ display: 'flex', justifyContent: 'center', margin: '20px 0' }} />;
};

export default Mermaid;
