import * as React from "react"

import { Button, type ButtonProps } from "@/components/ui/button"
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip"

interface AdminOnlyButtonProps extends ButtonProps {
  allowed: boolean
  tooltip?: string
}

function AdminOnlyButton({
  allowed,
  tooltip = "Admin role required.",
  disabled,
  ...props
}: AdminOnlyButtonProps) {
  if (allowed) {
    return <Button {...props} disabled={disabled} />
  }

  return (
    <TooltipProvider>
      <Tooltip>
        <TooltipTrigger asChild>
          <span className="inline-flex">
            <Button {...props} disabled />
          </span>
        </TooltipTrigger>
        <TooltipContent>{tooltip}</TooltipContent>
      </Tooltip>
    </TooltipProvider>
  )
}

export { AdminOnlyButton }
