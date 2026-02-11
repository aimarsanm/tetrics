'use client';

import React, { useState, useEffect } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { useToast } from '@/hooks/use-toast';
import { api, formatApiError } from '@/lib/api';
import type { Metric } from '@/lib/data';

interface AddMetricDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  criterionId: string;
  metric?: Metric | null;
  onSuccess: () => void;
}

export function AddMetricDialog({ 
  open, 
  onOpenChange, 
  criterionId,
  metric,
  onSuccess 
}: Readonly<AddMetricDialogProps>) {
  const { toast } = useToast();
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  const [name, setName] = useState('');
  const [definition, setDefinition] = useState('');
  const [unit, setUnit] = useState('Percent');
  const [scaleType, setScaleType] = useState<'nominal' | 'ordinal' | 'interval' | 'ratio'>('ratio');
  const [collectionMethod, setCollectionMethod] = useState<'automated' | 'manual' | 'hybrid'>('manual');
  const [weight, setWeight] = useState('1.0');
  const [targetValue, setTargetValue] = useState('');
  const [direction, setDirection] = useState<'maximize' | 'minimize'>('maximize');

  useEffect(() => {
    if (metric) {
      setName(metric.name || '');
      setDefinition(metric.definition || '');
      setUnit(metric.unit || 'Percent');
      setScaleType(metric.scaleType);
      setCollectionMethod(metric.collectionMethod as 'automated' | 'manual' | 'hybrid');
      setWeight(metric.weight.toString());
      setTargetValue(metric.targetValue?.toString() || '');
      setDirection(metric.direction);
    } else {
      setName('');
      setDefinition('');
      setUnit('Percent');
      setScaleType('ratio');
      setCollectionMethod('manual');
      setWeight('1.0');
      setTargetValue('');
      setDirection('maximize');
    }
  }, [metric, open]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);

    try {
      if (!name || !definition || !unit) {
        toast({
          title: 'Validation Error',
          description: 'Please fill in all required fields.',
          variant: 'destructive',
        });
        setIsSubmitting(false);
        return;
      }

      const weightNum = parseFloat(weight);
      if (isNaN(weightNum) || weightNum <= 0) {
        toast({
          title: 'Validation Error',
          description: 'Weight must be a positive number.',
          variant: 'destructive',
        });
        setIsSubmitting(false);
        return;
      }

      const targetValueNum = targetValue ? parseFloat(targetValue) : null;
      if (targetValue && isNaN(targetValueNum!)) {
        toast({
          title: 'Validation Error',
          description: 'Target value must be a valid number.',
          variant: 'destructive',
        });
        setIsSubmitting(false);
        return;
      }

      const metricData = {
        name,
        definition,
        unit,
        scale_type: scaleType,
        collection_method: collectionMethod,
        weight: weightNum,
        target_value: targetValueNum,
        direction: direction === 'maximize' ? 'higher_is_better' : 'lower_is_better',
        evaluation_criterion_id: criterionId,
      };

      if (metric) {
        await api.metrics.update(metric.id, metricData);
        toast({
          title: 'Success',
          description: 'Metric updated successfully.',
        });
      } else {
        await api.metrics.create(metricData);
        toast({
          title: 'Success',
          description: 'Metric created successfully.',
        });
      }

      onSuccess();
      onOpenChange(false);
    } catch (error) {
      console.error('Error saving metric:', error);
      const errorMessage = formatApiError(
        error,
        `Failed to ${metric ? 'update' : 'create'} metric. Please try again.`
      );
      
      toast({
        title: 'Error',
        description: errorMessage,
        variant: 'destructive',
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>{metric ? 'Edit Metric' : 'Add Metric'}</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit}>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="name">
                Name <span className="text-destructive">*</span>
              </Label>
              <Input
                id="name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="e.g., Response Accuracy"
                required
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="definition">
                Definition <span className="text-destructive">*</span>
              </Label>
              <Textarea
                id="definition"
                value={definition}
                onChange={(e) => setDefinition(e.target.value)}
                placeholder="Define how this metric is measured..."
                required
                rows={3}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="unit">
                Unit <span className="text-destructive">*</span>
              </Label>
              <Select value={unit} onValueChange={setUnit}>
                <SelectTrigger>
                  <SelectValue placeholder="Select unit type" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="Percent">Percent (%)</SelectItem>
                  <SelectItem value="Cardinal">Cardinal (count/number)</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="scaleType">
                  Scale Type <span className="text-destructive">*</span>
                </Label>
                <Select value={scaleType} onValueChange={(value: any) => setScaleType(value)}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="nominal">Nominal</SelectItem>
                    <SelectItem value="ordinal">Ordinal</SelectItem>
                    <SelectItem value="interval">Interval</SelectItem>
                    <SelectItem value="ratio">Ratio</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="collectionMethod">
                  Collection Method <span className="text-destructive">*</span>
                </Label>
                <Select value={collectionMethod} onValueChange={(value: any) => setCollectionMethod(value)}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="automated">Automated</SelectItem>
                    <SelectItem value="manual">Manual</SelectItem>
                    <SelectItem value="hybrid">Hybrid</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="weight">
                  Weight <span className="text-destructive">*</span>
                </Label>
                <Input
                  id="weight"
                  type="number"
                  step="0.1"
                  min="0"
                  value={weight}
                  onChange={(e) => setWeight(e.target.value)}
                  required
                />
                <p className="text-xs text-muted-foreground">
                  Relative importance within criterion
                </p>
              </div>
              <div className="space-y-2">
                <Label htmlFor="targetValue">Target Value (Optional)</Label>
                <Input
                  id="targetValue"
                  type="number"
                  step="any"
                  value={targetValue}
                  onChange={(e) => setTargetValue(e.target.value)}
                  placeholder="e.g., 95"
                />
              </div>
            </div>
            <div className="space-y-2">
              <Label htmlFor="direction">
                Direction <span className="text-destructive">*</span>
              </Label>
              <Select value={direction} onValueChange={(value: any) => setDirection(value)}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="maximize">Maximize (Higher is Better)</SelectItem>
                  <SelectItem value="minimize">Minimize (Lower is Better)</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={() => onOpenChange(false)}
              disabled={isSubmitting}
            >
              Cancel
            </Button>
            <Button type="submit" disabled={isSubmitting}>
              {isSubmitting ? 'Saving...' : metric ? 'Update Metric' : 'Create Metric'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
