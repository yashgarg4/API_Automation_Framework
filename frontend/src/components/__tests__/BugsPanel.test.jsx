import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import BugsPanel from "../BugsPanel";
import * as apiClient from "../../apiClient";

describe("BugsPanel", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it("asks user to login if no token", () => {
    render(<BugsPanel token={null} selectedProject={null} />);
    expect(
      screen.getByText(/Please login to manage bugs/i)
    ).toBeInTheDocument();
  });

  it("asks user to select a project if token but no project", () => {
    render(<BugsPanel token="fake-token" selectedProject={null} />);
    expect(
      screen.getByText(/Please select a project to view bugs/i)
    ).toBeInTheDocument();
  });

  it("renders bugs list when project and token defined", async () => {
    const mockBugs = [
      {
        id: 1,
        title: "Bug 1",
        description: "Desc 1",
        severity: "high",
        priority: "high",
        status: "open",
        project_id: 1,
        reporter_id: 1,
        assignee_id: null,
        created_at: "",
        updated_at: "",
      },
    ];

    vi.spyOn(apiClient, "apiGet").mockResolvedValueOnce(mockBugs);
    vi.spyOn(apiClient, "apiPost").mockResolvedValue({}); // for new bug
    vi.spyOn(apiClient, "apiPatch").mockResolvedValue({}); // for status change

    render(
      <BugsPanel
        token="fake-token"
        selectedProject={{ id: 1, name: "Project 1" }}
      />
    );

    // Trigger loading bugs
    const refreshButton = screen.getByTestId("load-bugs-button");
    refreshButton.click();

    const bugItem = await screen.findByTestId("bug-item");
    expect(bugItem).toHaveTextContent("Bug 1");
    expect(bugItem).toHaveTextContent("status: open");
  });
});
