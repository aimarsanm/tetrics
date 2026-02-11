'use client';

import React, { useState } from 'react';
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
import { TagInput } from '@/components/ui/tag-input';
import { ConversationHistoryInput } from '@/components/ui/conversation-history-input';
import { Switch } from '@/components/ui/switch';
import { useToast } from '@/hooks/use-toast';
import { formatApiError } from '@/lib/api';
import type { EvaluationCriterion, LLMToolConfiguration } from '@/lib/data';

interface LLMToolData {
  toolName: string;
  modelVersion: string;
  promptStrategy: string;
  parameters: Record<string, any>;
  timestamp: string;
  toolchain?: string;
  ide?: string;
  idePlugins?: string[];
  conversationHistory?: Array<{ role: string; content: string }>;
  skillsUsed?: string[];
}

interface AddLlmToolDialogProps {
  isOpen: boolean;
  onOpenChange: (isOpen: boolean) => void;
  onAddLlmTool: (data: LLMToolData) => Promise<void>;
  criteria: EvaluationCriterion[];
  editingTool?: LLMToolConfiguration;
  onUpdateLlmTool?: (toolId: string, data: LLMToolData) => Promise<void>;
}

export function AddLlmToolDialog({ 
  isOpen, 
  onOpenChange, 
  onAddLlmTool,
  criteria,
  editingTool,
  onUpdateLlmTool
}: Readonly<AddLlmToolDialogProps>) {
  const { toast } = useToast();
  const [toolName, setToolName] = useState('');
  const [modelVersion, setModelVersion] = useState('');
  const [promptStrategy, setPromptStrategy] = useState('');
  const [temperature, setTemperature] = useState('0.7');
  const [maxTokens, setMaxTokens] = useState('2048');
  const [timestamp, setTimestamp] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  // New ecosystem fields
  const [toolchain, setToolchain] = useState<string[]>([]);
  const [ide, setIde] = useState('');
  const [idePlugins, setIdePlugins] = useState<string[]>([]);
  
  // Prompt strategy enhancements
  const [useConversationHistory, setUseConversationHistory] = useState(false);
  const [conversationHistory, setConversationHistory] = useState<Array<{ role: string; content: string }>>([]);
  const [skillsUsed, setSkillsUsed] = useState<string[]>([]);

  // Update form when editingTool changes
  React.useEffect(() => {
    if (editingTool) {
      setToolName(editingTool.toolName);
      setModelVersion(editingTool.modelVersion);
      setPromptStrategy(editingTool.promptStrategy);
      setTemperature(editingTool.parameters?.temperature?.toString() || '0.7');
      setMaxTokens(editingTool.parameters?.max_tokens?.toString() || '2048');
      // Convert ISO timestamp to datetime-local format (YYYY-MM-DDTHH:mm)
      if (editingTool.timestamp) {
        const date = new Date(editingTool.timestamp);
        const localDateTime = new Date(date.getTime() - date.getTimezoneOffset() * 60000)
          .toISOString()
          .slice(0, 16);
        setTimestamp(localDateTime);
      }
      // New fields
      setToolchain(editingTool.toolchain ? editingTool.toolchain.split(',').map(t => t.trim()).filter(Boolean) : []);
      setIde(editingTool.ide || '');
      setIdePlugins(editingTool.idePlugins || []);
      setConversationHistory(editingTool.conversationHistory || []);
      setUseConversationHistory((editingTool.conversationHistory?.length || 0) > 0);
      setSkillsUsed(editingTool.skillsUsed || []);
    } else {
      // Reset form when not editing - set current date/time as default for new entries
      setToolName('');
      setModelVersion('');
      setPromptStrategy('');
      setTemperature('0.7');
      setMaxTokens('2048');
      // Set default timestamp to current date/time in local timezone
      const now = new Date();
      const localDateTime = new Date(now.getTime() - now.getTimezoneOffset() * 60000)
        .toISOString()
        .slice(0, 16);
      setTimestamp(localDateTime);
      // Reset new fields
      setToolchain([]);
      setIde('');
      setIdePlugins([]);
      setConversationHistory([]);
      setUseConversationHistory(false);
      setSkillsUsed([]);
    }
  }, [editingTool, isOpen]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (toolName.trim() && modelVersion.trim() && promptStrategy.trim() && timestamp.trim()) {
      setIsSubmitting(true);
      try {
        const parameters = {
          temperature: Number.parseFloat(temperature),
          max_tokens: Number.parseInt(maxTokens, 10),
        };
        
        // Convert datetime-local format to ISO timestamp
        const isoTimestamp = new Date(timestamp).toISOString();
        
        const toolData: LLMToolData = {
          toolName: toolName.trim(),
          modelVersion: modelVersion.trim(),
          promptStrategy: promptStrategy.trim(),
          parameters,
          timestamp: isoTimestamp,
          toolchain: toolchain.length > 0 ? toolchain.join(', ') : undefined,
          ide: ide || undefined,
          idePlugins: idePlugins.length > 0 ? idePlugins : undefined,
          conversationHistory: useConversationHistory && conversationHistory.length > 0 ? conversationHistory : undefined,
          skillsUsed: skillsUsed.length > 0 ? skillsUsed : undefined,
        };
        
        if (editingTool && onUpdateLlmTool) {
          // Update existing tool
          await onUpdateLlmTool(editingTool.id, toolData);
        } else {
          // Add new tool
          await onAddLlmTool(toolData);
        }
        
        // Reset form
        setToolName('');
        setModelVersion('');
        setPromptStrategy('');
        setTemperature('0.7');
        setMaxTokens('2048');
        setTimestamp('');
        setToolchain([]);
        setIde('');
        setIdePlugins([]);
        setConversationHistory([]);
        setUseConversationHistory(false);
        setSkillsUsed([]);
        onOpenChange(false);
      } catch (error) {
        console.error('Error saving LLM tool:', error);
        const errorMessage = formatApiError(
          error,
          'Failed to save LLM tool. Please try again.'
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
      <DialogContent className="sm:max-w-[700px] max-h-[90vh] flex flex-col">
        <DialogHeader>
          <DialogTitle>{editingTool ? 'Edit LLM Tool Configuration' : 'Add LLM Tool Configuration'}</DialogTitle>
          <DialogDescription>
            {editingTool 
              ? 'Update the details for the LLM tool configuration.'
              : 'Enter the details for the new LLM tool configuration.'}
          </DialogDescription>
        </DialogHeader>
        
        <form onSubmit={handleSubmit} className="flex flex-col flex-1 overflow-hidden">
          <div className="flex-1 overflow-y-auto px-1">
            <div className="space-y-6 py-4">
              {/* Basic Configuration */}
              <div className="space-y-4">
                <h4 className="text-sm font-semibold text-muted-foreground">Basic Configuration</h4>
                
                <div className="space-y-2">
                  <Label htmlFor="tool-name">Tool Name <span className="text-destructive">*</span></Label>
                  <Input
                    id="tool-name"
                    value={toolName}
                    onChange={(e) => setToolName(e.target.value)}
                    placeholder="e.g., GitHub Copilot"
                    required
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="model-version">Model Version <span className="text-destructive">*</span></Label>
                  <Input
                    id="model-version"
                    value={modelVersion}
                    onChange={(e) => setModelVersion(e.target.value)}
                    placeholder="e.g., gpt-4-turbo-2024-04-09"
                    required
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="prompt-strategy">Prompt Strategy <span className="text-destructive">*</span></Label>
                  <Textarea
                    id="prompt-strategy"
                    value={promptStrategy}
                    onChange={(e) => setPromptStrategy(e.target.value)}
                    placeholder="Describe the prompt strategy..."
                    required
                    rows={3}
                  />
                </div>
                
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="temperature">Temperature <span className="text-destructive">*</span></Label>
                    <Input
                      id="temperature"
                      type="number"
                      step="0.1"
                      min="0"
                      max="2"
                      value={temperature}
                      onChange={(e) => setTemperature(e.target.value)}
                      required
                    />
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="max-tokens">Max Tokens <span className="text-destructive">*</span></Label>
                    <Input
                      id="max-tokens"
                      type="number"
                      min="1"
                      value={maxTokens}
                      onChange={(e) => setMaxTokens(e.target.value)}
                      required
                    />
                  </div>
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="timestamp">Timestamp <span className="text-destructive">*</span></Label>
                  <Input
                    id="timestamp"
                    type="datetime-local"
                    value={timestamp}
                    onChange={(e) => setTimestamp(e.target.value)}
                    required
                  />
                </div>
              </div>
              
              {/* Ecosystem Context Section */}
              <div className="space-y-4 border-t pt-4">
                <h4 className="text-sm font-semibold text-muted-foreground">Ecosystem Context</h4>
                
                <div className="space-y-2">
                  <Label htmlFor="toolchain">Toolchain</Label>
                  <TagInput
                    value={toolchain}
                    onChange={setToolchain}
                    placeholder="e.g., LangSmith, LangChain, Ollama..."
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="ide">IDE</Label>
                  <Input
                    id="ide"
                    value={ide}
                    onChange={(e) => setIde(e.target.value)}
                    placeholder="e.g., VS Code"
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="ide-plugins">IDE Plugins</Label>
                  <TagInput
                    value={idePlugins}
                    onChange={setIdePlugins}
                    placeholder="Type plugin name and press Enter..."
                  />
                </div>
              </div>
              
              {/* Prompt Strategy Enhancements */}
              <div className="space-y-4 border-t pt-4">
                <h4 className="text-sm font-semibold text-muted-foreground">Prompt Strategy Enhancements</h4>
                
                <div className="flex items-center space-x-2">
                  <Switch
                    id="use-conversation"
                    checked={useConversationHistory}
                    onCheckedChange={setUseConversationHistory}
                  />
                  <Label htmlFor="use-conversation" className="cursor-pointer">
                    Use Conversation History
                  </Label>
                  <span className="text-sm text-muted-foreground">
                    ({useConversationHistory ? 'Multi-turn dialogue' : 'Single prompt'})
                  </span>
                </div>
                
                {useConversationHistory && (
                  <div className="space-y-2">
                    <Label>Conversation</Label>
                    <ConversationHistoryInput
                      value={conversationHistory}
                      onChange={setConversationHistory}
                    />
                  </div>
                )}
                
                <div className="space-y-2">
                  <Label htmlFor="skills-used">Skills Used</Label>
                  <TagInput
                    value={skillsUsed}
                    onChange={setSkillsUsed}
                    placeholder="e.g., open-ended questioning, contextual framing..."
                  />
                </div>
              </div>
            </div>
          </div>
          
          <DialogFooter className="mt-4">
            <DialogClose asChild>
              <Button type="button" variant="outline" disabled={isSubmitting}>
                Cancel
              </Button>
            </DialogClose>
            <Button type="submit" disabled={isSubmitting}>
              {(() => {
                if (isSubmitting) {
                  return editingTool ? 'Updating...' : 'Adding...';
                }
                return editingTool ? 'Update Configuration' : 'Add Configuration';
              })()}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
