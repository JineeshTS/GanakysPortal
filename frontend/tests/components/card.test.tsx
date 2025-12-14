/**
 * Card Component Tests
 * WBS Reference: Task 30.1.2.1.2
 */
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  CardFooter,
} from '@/components/ui/card';

describe('Card Component', () => {
  it('renders card with all subcomponents', () => {
    render(
      <Card data-testid="card">
        <CardHeader>
          <CardTitle>Card Title</CardTitle>
          <CardDescription>Card Description</CardDescription>
        </CardHeader>
        <CardContent>Card Content</CardContent>
        <CardFooter>Card Footer</CardFooter>
      </Card>
    );

    expect(screen.getByTestId('card')).toBeInTheDocument();
    expect(screen.getByText('Card Title')).toBeInTheDocument();
    expect(screen.getByText('Card Description')).toBeInTheDocument();
    expect(screen.getByText('Card Content')).toBeInTheDocument();
    expect(screen.getByText('Card Footer')).toBeInTheDocument();
  });

  it('renders card with proper styling', () => {
    render(<Card data-testid="card">Content</Card>);

    const card = screen.getByTestId('card');
    expect(card).toHaveClass('rounded-xl', 'border', 'bg-card');
  });

  it('renders CardHeader with proper spacing', () => {
    render(
      <Card>
        <CardHeader data-testid="header">Header</CardHeader>
      </Card>
    );

    const header = screen.getByTestId('header');
    expect(header).toHaveClass('flex', 'flex-col', 'space-y-1.5', 'p-6');
  });

  it('renders CardTitle with proper typography', () => {
    render(
      <Card>
        <CardHeader>
          <CardTitle data-testid="title">Title</CardTitle>
        </CardHeader>
      </Card>
    );

    const title = screen.getByTestId('title');
    expect(title).toHaveClass('font-semibold', 'leading-none');
  });

  it('renders CardDescription with muted text', () => {
    render(
      <Card>
        <CardHeader>
          <CardDescription data-testid="description">Description</CardDescription>
        </CardHeader>
      </Card>
    );

    const description = screen.getByTestId('description');
    expect(description).toHaveClass('text-sm', 'text-muted-foreground');
  });

  it('renders CardContent with proper padding', () => {
    render(
      <Card>
        <CardContent data-testid="content">Content</CardContent>
      </Card>
    );

    const content = screen.getByTestId('content');
    expect(content).toHaveClass('p-6', 'pt-0');
  });

  it('renders CardFooter with flex layout', () => {
    render(
      <Card>
        <CardFooter data-testid="footer">Footer</CardFooter>
      </Card>
    );

    const footer = screen.getByTestId('footer');
    expect(footer).toHaveClass('flex', 'items-center', 'p-6', 'pt-0');
  });

  it('accepts custom className for all subcomponents', () => {
    render(
      <Card className="custom-card" data-testid="card">
        <CardHeader className="custom-header" data-testid="header">
          <CardTitle className="custom-title" data-testid="title">Title</CardTitle>
          <CardDescription className="custom-desc" data-testid="desc">Description</CardDescription>
        </CardHeader>
        <CardContent className="custom-content" data-testid="content">Content</CardContent>
        <CardFooter className="custom-footer" data-testid="footer">Footer</CardFooter>
      </Card>
    );

    expect(screen.getByTestId('card')).toHaveClass('custom-card');
    expect(screen.getByTestId('header')).toHaveClass('custom-header');
    expect(screen.getByTestId('title')).toHaveClass('custom-title');
    expect(screen.getByTestId('desc')).toHaveClass('custom-desc');
    expect(screen.getByTestId('content')).toHaveClass('custom-content');
    expect(screen.getByTestId('footer')).toHaveClass('custom-footer');
  });
});
