export function removeReviewedCandidate(state, candidateId) {
  if (!candidateId) return { ...state, candidates: [...(state.candidates || [])] };
  const candidates = (state.candidates || []).filter(candidate => candidate.id !== candidateId);
  return {
    ...state,
    candidates,
    message: `Reviewed candidate accepted. ${candidates.length} candidate${candidates.length === 1 ? '' : 's'} remaining in this First Pass queue.`,
  };
}
