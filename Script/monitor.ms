try(PipelineMonitor.Stop())catch()
global PipelineMonitor = undefined
gc()
global pipeDir = (sysInfo.tempdir + "3dsMaxPipeline\\")
global cmdFile = pipeDir + "command.ms"
global resFile = pipeDir + "result.txt"

makeDir pipeDir all:true

global CheckPipe
fn CheckPipe source args = (
    if (dotNetClass "System.IO.File").Exists cmdFile do (
        try (
            local content = (dotNetClass "System.IO.File").ReadAllText cmdFile
            deleteFile cmdFile
            
            local result = execute content
            
            if result == undefined then result = "OK"
            (dotNetClass "System.IO.File").WriteAllText resFile (result as string)
            
            print ("Pipeline Executed: " + (substring content 1 (amin 50 content.count)))
        )
        catch (
            local err = getCurrentException()
            print ("Pipeline Error: " + err)
            (dotNetClass "System.IO.File").WriteAllText resFile ("ERROR: " + err)
        )
    )
)

PipelineMonitor = dotNetObject "System.Windows.Forms.Timer"
PipelineMonitor.Interval = 100
dotnet.addEventHandler PipelineMonitor "Tick" CheckPipe
PipelineMonitor.Start()

clearListener()
print "--- PIPELINE MONITOR READY ---"
print ("Listening at: " + pipeDir)