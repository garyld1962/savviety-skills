namespace BlazorStack.Shared.Scoring;

/// <summary>
/// Implement this interface to provide domain-specific scoring logic.
/// Scoring should be computed on read, never stored in the database.
/// </summary>
public interface IScoringService<T> where T : class
{
    double ComputeScore(T item);
}
