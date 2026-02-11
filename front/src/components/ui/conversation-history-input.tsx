'use client';

import React from 'react';
import { Plus, Trash2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Card, CardContent } from '@/components/ui/card';

interface ConversationMessage {
  role: string;
  content: string;
}

interface ConversationHistoryInputProps {
  value: ConversationMessage[];
  onChange: (messages: ConversationMessage[]) => void;
  disabled?: boolean;
}

export function ConversationHistoryInput({ 
  value = [], 
  onChange,
  disabled = false
}: Readonly<ConversationHistoryInputProps>) {
  const addMessage = () => {
    onChange([...value, { role: 'user', content: '' }]);
  };

  const removeMessage = (index: number) => {
    onChange(value.filter((_, i) => i !== index));
  };

  const updateMessage = (index: number, field: 'role' | 'content', newValue: string) => {
    const updated = value.map((msg, i) => 
      i === index ? { ...msg, [field]: newValue } : msg
    );
    onChange(updated);
  };

  return (
    <div className="space-y-3">
      {value.map((message, index) => (
        <Card key={index} className="border-dashed">
          <CardContent className="pt-4">
            <div className="flex gap-2 mb-2">
              <div className="flex-1">
                <Label htmlFor={`role-${index}`} className="text-xs">Role</Label>
                <Select
                  value={message.role}
                  onValueChange={(val) => updateMessage(index, 'role', val)}
                  disabled={disabled}
                >
                  <SelectTrigger id={`role-${index}`} className="h-8">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="user">User</SelectItem>
                    <SelectItem value="assistant">Assistant</SelectItem>
                    <SelectItem value="system">System</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <Button
                type="button"
                variant="ghost"
                size="icon"
                onClick={() => removeMessage(index)}
                disabled={disabled}
                className="mt-5 h-8 w-8"
              >
                <Trash2 className="h-4 w-4" />
              </Button>
            </div>
            <div>
              <Label htmlFor={`content-${index}`} className="text-xs">Message</Label>
              <Textarea
                id={`content-${index}`}
                value={message.content}
                onChange={(e) => updateMessage(index, 'content', e.target.value)}
                placeholder="Enter message content..."
                disabled={disabled}
                rows={2}
                className="resize-none"
              />
            </div>
          </CardContent>
        </Card>
      ))}
      <Button
        type="button"
        variant="outline"
        size="sm"
        onClick={addMessage}
        disabled={disabled}
        className="w-full"
      >
        <Plus className="h-4 w-4 mr-2" />
        Add Message
      </Button>
    </div>
  );
}
