-- File Monitor for Pipeline Commands
global pipelineMonitorTimer = undefined
global commandFile = "D:/Puoli/An3 Sem1 - UL/Graphics/Pipeline-for-Unreal-Engine/temp/command.ms"
global resultFile = "D:/Puoli/An3 Sem1 - UL/Graphics/Pipeline-for-Unreal-Engine/temp/result.txt"

fn checkForCommands = (
    if doesFileExist commandFile then (
        try (
            -- Execute the command file
            local result = fileIn commandFile
            
            -- Write result
            local f = createFile resultFile
            if result != undefined then (
                format "%\n" (result as string) to:f
            ) else (
                format "OK\n" to:f
            )
            close f
            
            -- Delete command file
            deleteFile commandFile
            
        ) catch (
            local f = createFile resultFile
            format "ERROR: %\n" (getCurrentException() as string) to:f
            close f
            deleteFile commandFile
        )
    )
)

-- Setup timer
if pipelineMonitorTimer != undefined then (
    stopTimer pipelineMonitorTimer
)

pipelineMonitorTimer = dotNetObject "System.Windows.Forms.Timer"
pipelineMonitorTimer.Interval = 100
dotNet.addEventHandler pipelineMonitorTimer "Tick" checkForCommands
pipelineMonitorTimer.Start()

print "========================================"
print "Pipeline File Monitor Started"
print "Checking: temp/command.ms every 100ms"
print "========================================"