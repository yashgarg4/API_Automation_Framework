import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import AuthSection from "../AuthSection";

const mockFetch = vi.fn();

describe("AuthSection", () => {
  beforeEach(() => {
    mockFetch.mockReset();
    global.fetch = mockFetch;
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("renders register and login forms", () => {
    render(<AuthSection onLoginSuccess={() => {}} />);

    // Use headings instead of generic text, this avoids ambiguity
    expect(
      screen.getByRole("heading", { name: /Register/i })
    ).toBeInTheDocument();

    expect(screen.getByRole("heading", { name: /Login/i })).toBeInTheDocument();

    // Optionally assert inputs/buttons exist:
    expect(screen.getByTestId("register-email")).toBeInTheDocument();
    expect(screen.getByTestId("login-email")).toBeInTheDocument();
  });

  it("calls onLoginSuccess when login is successful", async () => {
    const onLoginSuccess = vi.fn();

    // Mock login response
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ access_token: "fake-token", token_type: "bearer" }),
    });

    render(<AuthSection onLoginSuccess={onLoginSuccess} />);

    fireEvent.change(screen.getByTestId("login-email"), {
      target: { value: "user@example.com" },
    });
    fireEvent.change(screen.getByTestId("login-password"), {
      target: { value: "password" },
    });

    fireEvent.click(screen.getByTestId("login-button"));

    await waitFor(() => {
      expect(onLoginSuccess).toHaveBeenCalledWith(
        "fake-token",
        "user@example.com"
      );
    });
  });
});
