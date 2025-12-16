/**
 * Input Component Tests
 * WBS Reference: Task 30.1.2.1.2
 */
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { Input } from '@/components/ui/input';

describe('Input Component', () => {
  it('renders with default type', () => {
    render(<Input placeholder="Enter text" />);

    const input = screen.getByPlaceholderText(/enter text/i);
    expect(input).toBeInTheDocument();
    expect(input).toHaveAttribute('type', 'text');
  });

  it('renders with different types', () => {
    const { rerender } = render(<Input type="email" data-testid="input" />);
    expect(screen.getByTestId('input')).toHaveAttribute('type', 'email');

    rerender(<Input type="password" data-testid="input" />);
    expect(screen.getByTestId('input')).toHaveAttribute('type', 'password');

    rerender(<Input type="number" data-testid="input" />);
    expect(screen.getByTestId('input')).toHaveAttribute('type', 'number');

    rerender(<Input type="date" data-testid="input" />);
    expect(screen.getByTestId('input')).toHaveAttribute('type', 'date');
  });

  it('handles value changes', () => {
    const handleChange = vi.fn();
    render(<Input onChange={handleChange} data-testid="input" />);

    const input = screen.getByTestId('input');
    fireEvent.change(input, { target: { value: 'test value' } });

    expect(handleChange).toHaveBeenCalledTimes(1);
  });

  it('displays controlled value', () => {
    render(<Input value="controlled" readOnly data-testid="input" />);

    const input = screen.getByTestId('input');
    expect(input).toHaveValue('controlled');
  });

  it('can be disabled', () => {
    render(<Input disabled data-testid="input" />);

    const input = screen.getByTestId('input');
    expect(input).toBeDisabled();
  });

  it('applies custom className', () => {
    render(<Input className="custom-input" data-testid="input" />);

    const input = screen.getByTestId('input');
    expect(input).toHaveClass('custom-input');
  });

  it('has required styling classes', () => {
    render(<Input data-testid="input" />);

    const input = screen.getByTestId('input');
    expect(input).toHaveClass('flex', 'h-9', 'w-full', 'rounded-md', 'border');
  });

  it('supports ref forwarding', () => {
    const ref = vi.fn();
    render(<Input ref={ref} />);

    expect(ref).toHaveBeenCalled();
  });

  it('handles focus and blur events', () => {
    const handleFocus = vi.fn();
    const handleBlur = vi.fn();

    render(<Input onFocus={handleFocus} onBlur={handleBlur} data-testid="input" />);

    const input = screen.getByTestId('input');

    fireEvent.focus(input);
    expect(handleFocus).toHaveBeenCalledTimes(1);

    fireEvent.blur(input);
    expect(handleBlur).toHaveBeenCalledTimes(1);
  });

  it('accepts aria attributes', () => {
    render(
      <Input
        aria-label="test input"
        aria-describedby="help-text"
        data-testid="input"
      />
    );

    const input = screen.getByTestId('input');
    expect(input).toHaveAttribute('aria-label', 'test input');
    expect(input).toHaveAttribute('aria-describedby', 'help-text');
  });
});
