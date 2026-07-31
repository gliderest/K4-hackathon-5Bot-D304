import type { Citation } from "../types/api";

type CitationLinkProps = {
  citation: Citation;
  onOpen: (citation: Citation) => void;
};

export function CitationLink({ citation, onOpen }: CitationLinkProps) {
  return (
    <a
      className="citation-link"
      href={citation.viewer_path}
      onClick={(event) => {
        event.preventDefault();
        onOpen(citation);
      }}
    >
      <span>{citation.label}</span>
      <small>{citation.score ? `độ khớp ${citation.score}` : citation.source_type}</small>
    </a>
  );
}
