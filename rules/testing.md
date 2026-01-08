---
globs: ["**/*.test.ts", "**/*.spec.ts", "**/__tests__/**"]
---

# Testing Rules

## Structure
- Use BDD-style comments: `#given`, `#when`, `#then`
- One logical assertion per test
- Descriptive test names that explain the scenario

## Mocking
- Mock external dependencies (APIs, databases)
- Never mock the code under test
- Reset mocks between tests

## Coverage
- Test happy path
- Test error scenarios
- Test edge cases (empty, null, boundary values)
- Test async states (loading, success, error)

## Example
```typescript
describe('UserService', () => {
  it('should return user when found', async () => {
    // #given
    const mockUser = { id: '1', name: 'Test' };
    mockDb.findUser.mockResolvedValue(mockUser);

    // #when
    const result = await userService.getUser('1');

    // #then
    expect(result).toEqual(mockUser);
  });
});
```
