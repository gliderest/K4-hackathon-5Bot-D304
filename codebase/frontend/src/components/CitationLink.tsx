import type { Citation } from "../types/api";

type CitationLinkProps = {
  citation: Citation;
};

export function CitationLink({ citation }: CitationLinkProps) {
  return (
    <a className="citation-link" href={citation.viewer_path} target="_blank" rel="noreferrer">
      <span>{citation.label}</span>
      <small>{citation.score ? `độ khớp ${citation.score}` : citation.source_type}</small>
    </a>
  );
}
