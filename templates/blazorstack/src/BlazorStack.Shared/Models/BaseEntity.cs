namespace BlazorStack.Shared.Models;

public interface IEntity
{
    string Id { get; }
    DateTime CreatedAt { get; }
    DateTime UpdatedAt { get; }
}
