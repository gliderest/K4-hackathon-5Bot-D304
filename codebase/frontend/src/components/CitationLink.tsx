import type { Citation } from "../types/api";

type CitationLinkProps = {
  citation: Citation;
  onOpen: (citation: Citation) => void;
};

export function CitationLink({ citation, onOpen }: CitationLinkProps) {
  if (citation.source_type === "web") {
    return (
      <a
        className="citation-link"
        href={citation.viewer_path}
        target="_blank"
        rel="noreferrer"
      >
        <span>{citation.label}</span>
        <small>Nguồn web</small>
      </a>
    );
  }

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
