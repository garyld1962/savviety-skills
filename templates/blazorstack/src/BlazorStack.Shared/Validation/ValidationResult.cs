namespace BlazorStack.Shared.Validation;

public sealed record ValidationResult(
    bool IsValid,
    string? Error = null,
    Dictionary<string, string>? Fields = null)
{
    public static ValidationResult Success() => new(true);

    public static ValidationResult Failure(string error, Dictionary<string, string>? fields = null)
        => new(false, error, fields);
}
