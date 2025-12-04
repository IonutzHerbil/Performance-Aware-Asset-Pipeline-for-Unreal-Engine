global pipelineTempDir = sysInfo.tempdir + "3dsMaxPipeline\\"
makeDir pipelineTempDir

cmdFile = pipelineTempDir + "command.ms"
resultFile = pipelineTempDir + "result.txt"

print "--- PIPELINE MONITOR STARTED ---"
print ("Listening at: " + pipelineTempDir)

fn checkForCommand = (
    if doesFileExist cmdFile do (
        try (
            local f = openFile cmdFile
            local cmd = ""
            while not eof f do cmd += readLine f
            close f
            
            deleteFile cmdFile
            
            print ("Executing: " + cmd)
            
            local result = ""
            try (
                result = (execute cmd) as string
            ) catch (
                result = "ERROR: " + (getCurrentException())
            )
            
            local out = createFile resultFile
            format "%" result to:out
            close out
            
            print ("Result Sent.")
            
        ) catch (
        )
    )
)


try(pipelineTimer.Stop())catch() 

pipelineTimer = dotNetObject "System.Windows.Forms.Timer"
pipelineTimer.interval = 200 
dotnet.addEventHandler pipelineTimer "tick" checkForCommand
pipelineTimer.start()

print "--- MONITOR RUNNING ---"