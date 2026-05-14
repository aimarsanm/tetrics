'use client';

import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
  DialogClose,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '../ui/textarea';
import { formatApiError } from '@/lib/api';
import { useToast } from '@/hooks/use-toast';
import type { Measurement } from '@/lib/data';

interface AddMeasurementDialogProps {
  isOpen: boolean;
  onOpenChange: (isOpen: boolean) => void;
  onAddMeasurement: (
    value: number,
    notes: string,
    llmToolConfigId: string,
    metricId: string
  ) => Promise<void>;
  llmToolConfigId: string;
  metricId: string;
  metricName: string;
  toolName: string;
  existingMeasurement?: Measurement;
  evaluator: string;
}

export function AddMeasurementDialog({
  isOpen,
  onOpenChange,
  onAddMeasurement,
  llmToolConfigId,
  metricId,
  metricName,
  toolName,
  existingMeasurement,
  evaluator,
}: Readonly<AddMeasurementDialogProps>) {
  const [value, setValue] = useState('');
  const [notes, setNotes] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const { toast } = useToast();

  // Pre-fill form when editing existing measurement
  useEffect(() => {
    if (existingMeasurement) {
      setValue(String(existingMeasurement.value));
      setNotes(existingMeasurement.notes || '');
    } else {
      setValue('');
      setNotes('');
    }
  }, [existingMeasurement, isOpen]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (value.trim()) {
      setIsSubmitting(true);
      try {
        await onAddMeasurement(
          parseFloat(value),
          notes.trim(),
          llmToolConfigId,
          metricId
        );

        // Reset form
        setValue('');
        setNotes('');
        onOpenChange(false);
      } catch (error) {
        console.error('Error adding measurement:', error);
        const errorMessage = formatApiError(
          error,
          'Failed to add measurement. Please try again.'
        );

        toast({
          title: 'Error',
          description: errorMessage,
          variant: 'destructive',
        });
      } finally {
        setIsSubmitting(false);
      }
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[425px]">
        <form onSubmit={handleSubmit}>
          <DialogHeader>
            <DialogTitle>{existingMeasurement ? 'Edit Measurement' : 'Add Measurement'}</DialogTitle>
            <DialogDescription>
              {existingMeasurement ? 'Update the' : 'Add a'} measurement for <strong>{metricName}</strong> using <strong>{toolName}</strong>
            </DialogDescription>
          </DialogHeader>
          <div className="grid gap-4 py-4">
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="value" className="text-right">
                Value
              </Label>
              <Input
                id="value"
                type="number"
                step="any"
                value={value}
                onChange={(e) => setValue(e.target.value)}
                className="col-span-3"
                placeholder="e.g., 85.5"
                required
              />
            </div>
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="evaluator" className="text-right">
                Evaluator
              </Label>
              <Input
                id="evaluator"
                value={evaluator}
                className="col-span-3 bg-muted text-muted-foreground"
                disabled
                readOnly
              />
            </div>
            <div className="grid grid-cols-4 items-start gap-4">
              <Label htmlFor="notes" className="text-right pt-2">
                Notes
              </Label>
              <Textarea
                id="notes"
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                className="col-span-3"
                placeholder="Optional notes about this measurement..."
                rows={3}
              />
            </div>
          </div>
          <DialogFooter>
            <DialogClose asChild>
              <Button type="button" variant="outline" disabled={isSubmitting}>
                Cancel
              </Button>
            </DialogClose>
            <Button type="submit" disabled={isSubmitting}>
              {isSubmitting ? (existingMeasurement ? 'Updating...' : 'Adding...') : (existingMeasurement ? 'Update Measurement' : 'Add Measurement')}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
