'use client';

import * as React from 'react';
import { CalendarIcon } from 'lucide-react';
import { format } from 'date-fns';
import { DateRange } from 'react-day-picker';

import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { Calendar } from '@/components/ui/calendar';
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover';

interface DateFilterProps {
  dateRange: DateRange | undefined;
  onDateRangeChange: (range: DateRange | undefined) => void;
  className?: string;
}

export function DateFilter({ dateRange, onDateRangeChange, className }: Readonly<DateFilterProps>) {
  const getDateRangeText = () => {
    if (!dateRange?.from) {
      return <span>Pick a date range</span>;
    }
    if (dateRange.to) {
      return (
        <>
          {format(dateRange.from, 'LLL dd, y')} -{' '}
          {format(dateRange.to, 'LLL dd, y')}
        </>
      );
    }
    return format(dateRange.from, 'LLL dd, y');
  };

  return (
    <div className={cn('grid gap-2', className)}>
      <Popover>
        <PopoverTrigger asChild>
          <Button
            id="date"
            variant={'outline'}
            className={cn(
              'w-[300px] justify-start text-left font-normal',
              !dateRange && 'text-muted-foreground'
            )}
          >
            <CalendarIcon className="mr-2 h-4 w-4" />
            {getDateRangeText()}
          </Button>
        </PopoverTrigger>
        <PopoverContent className="w-auto p-0" align="start">
          <Calendar
            initialFocus
            mode="range"
            defaultMonth={dateRange?.from}
            selected={dateRange}
            onSelect={onDateRangeChange}
            numberOfMonths={2}
          />
          {dateRange && (
            <div className="p-3 border-t">
              <Button
                variant="ghost"
                className="w-full"
                onClick={() => onDateRangeChange(undefined)}
              >
                Clear Filter
              </Button>
            </div>
          )}
        </PopoverContent>
      </Popover>
    </div>
  );
}
