import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import ProjectsPanel from "../ProjectsPanel";
import * as apiClient from "../../apiClient";

describe("ProjectsPanel", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it("shows login message when no token", () => {
    render(
      <ProjectsPanel
        token={null}
        selectedProject={null}
        onSelectProject={() => {}}
      />
    );

    expect(
      screen.getByText(/Please login to manage projects/i)
    ).toBeInTheDocument();
  });

  it("renders projects from API when token provided", async () => {
    const mockProjects = [
      { id: 1, name: "Project A", description: "Desc A", owner_id: 1 },
      { id: 2, name: "Project B", description: "Desc B", owner_id: 1 },
    ];

    vi.spyOn(apiClient, "apiGet").mockResolvedValueOnce(mockProjects);
    vi.spyOn(apiClient, "apiPost").mockResolvedValue({}); // used when creating project

    render(
      <ProjectsPanel
        token="fake-token"
        selectedProject={null}
        onSelectProject={() => {}}
      />
    );

    // manually trigger refresh
    fireEvent.click(screen.getByTestId("load-projects-button"));

    // Wait for list
    const projectItems = await screen.findAllByTestId("project-item");
    expect(projectItems).toHaveLength(2);
    expect(projectItems[0]).toHaveTextContent("Project A");
    expect(projectItems[1]).toHaveTextContent("Project B");
  });
});
