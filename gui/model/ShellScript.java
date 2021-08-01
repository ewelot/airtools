/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package tl.airtoolsgui.model;

import java.io.File;
import java.io.IOException;
import java.util.Map;
import javafx.concurrent.Task;

/**
 *
 * @author lehmann
 */
public class ShellScript {
    
    private String fileName;
    private String addPath="";
    private String envVars="";
    private String opts="";
    private String args="";
    private String workingDir="";
    private Process process;
    private int exitCode;
    private SimpleLogger logger;

    public void setLog(SimpleLogger logger) {
        this.logger = logger;
    }

    public String getFileName() {
        return fileName;
    }

    public void setFileName(String fileName) {
        this.fileName = fileName;
    }
    
    public void setAddPath(String addPath) {
        this.addPath = addPath;
    }

    public void setEnvVars(String vars) {
        this.envVars = vars;
    }

    public void setOpts(String opts) {
        this.opts = opts;
    }

    public void setArgs(String args) {
        this.args = args;
    }

    public void setWorkingDir(String workingDir) {
        this.workingDir = workingDir;
    }

    public long getPID() {
        return process.pid();
    }
    
    public int getExitCode() {
        return exitCode;
    }

    public void runFunction(String funcName) {
        String command;
        exitCode=255;
        String cmdDescription = funcName;
        
        if (args != null && args.equals("-c")) cmdDescription = "User command";
        
        //logger.log("runFunction " + funcName);
        if (process != null && process.isAlive()) {
            logger.log("WARNING: task not started, another process is running.");
            return;
        }
        command=envVars + " " + getFileName() + " " + opts + " " + funcName + " " + args;
        System.out.println("ShellScript.runFunction: command = " + command);
        ProcessBuilder pb = new ProcessBuilder("/bin/bash", "-c", command);
        Map<String, String> envs = pb.environment();
        envs.put("PATH", ".:" + envs.get("PATH"));
        
        // add current working directory to PATH
        
        if (! workingDir.isEmpty()) {
            File file = new File(workingDir);
            if (file.isDirectory()) { 
                pb.directory(new File(workingDir));
            } else {
                logger.log("ERROR: directory " + workingDir + " does not exist.");
                return;
            }
        }
        if (! addPath.isEmpty()) {
            envs = pb.environment();
            String path = addPath + ':' + envs.get("PATH");
            System.out.println("new PATH=" + path);
            envs.put("PATH", path);
        }
        try {
            //pb.inheritIO();
            process = pb.start();
            /*
            BufferedReader input = new BufferedReader (
                    new InputStreamReader(process.getInputStream()));
            String line;
            while ((line = input.readLine()) != null) {
                logger.log(line);  
            }
            input.close();  
            */
            
            Task grabIO = new Task<Void>() {
                                @Override
                protected Void call() {
                    //StreamGobbler stdinGobbler = new StreamGobbler(
                    //    process.getOutputStream(), System.in::read);
                    StreamGobbler stdoutGobbler = new StreamGobbler(
                        process.getInputStream(), logger::log);
                    StreamGobbler stderrGobbler = new StreamGobbler(
                        process.getErrorStream(), logger::log);
                    stdoutGobbler.run();
                    stderrGobbler.run();
                    return null;
                }

            };
            Thread thread = new Thread(grabIO);
            thread.setDaemon(true);
            thread.start();
            
            exitCode = process.waitFor();
            logger.log("# " + cmdDescription + " finished with exitCode=" + exitCode);
        } catch (IOException ex) {
            //Logger.getLogger(ShellScript.class.getName()).log(Level.SEVERE, null, ex);
            logger.log(ex);
            logger.log("# " + cmdDescription + " IOException");
        } catch (InterruptedException ex) {
            //Logger.getLogger(ShellScript.class.getName()).log(Level.SEVERE, null, ex);
            logger.log("# " + cmdDescription + " interrupted");
            //logger.log(ex);
            exitCode=255;
        }
    }
    
    public int killProcess () {
        System.out.println("running killProcess() on " + process.pid());
        int exitCodeKill = 0;
        if (process.isAlive()) {
            String command=envVars + " " + getFileName() + " kill " + process.pid();
            System.out.println("ShellScript.killProcess: command = " + command);
            ProcessBuilder pbKill = new ProcessBuilder("/bin/bash", "-c", command);
            Map<String, String> envsKill = pbKill.environment();
            envsKill.put("PATH", ".:" + envsKill.get("PATH"));
        
            if (! addPath.isEmpty()) {
                envsKill = pbKill.environment();
                String path = addPath + ':' + envsKill.get("PATH");
                System.out.println("new PATH=" + path);
                envsKill.put("PATH", path);
            }
            pbKill.directory(new File(workingDir));
            
            try {
                Process pKill=pbKill.start();
                exitCodeKill=pKill.waitFor();
                logger.log("# Process killed upon user request");
            } catch (IOException ex) {
                //Logger.getLogger(ShellScript.class.getName()).log(Level.SEVERE, null, ex);
                logger.log(ex);
                logger.log("# killProcess failed with IOException (pid=" + process.pid() + ")");
            } catch (InterruptedException exInt) {
                //Logger.getLogger(ShellScript.class.getName()).log(Level.SEVERE, null, exInt);
                logger.log(exInt);
                logger.log("# killProcess interrupted (pid=" + process.pid() + ")");
            }
        }
        
        return exitCodeKill;
    }
}
