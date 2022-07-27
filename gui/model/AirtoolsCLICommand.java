/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package tl.airtoolsgui.model;

import java.util.logging.Level;
import java.util.logging.Logger;
import javafx.beans.property.BooleanProperty;
import javafx.beans.property.SimpleBooleanProperty;
import javafx.concurrent.Task;
import javafx.scene.control.Button;

/**
 *
 * @author lehmann
 */
public class AirtoolsCLICommand {
    
    private String cmdName;
    private String[] opts = new String[0];
    private String[] args = new String[0];
    private final Button btnStart;

    private final SimpleLogger logger;
    private final ShellScript sh;
    private Task task;
    private Thread thread;
    private BooleanProperty isRunning;
    private int exitcode;
    private String resultString;

    public AirtoolsCLICommand(String cmdName, Button btn, SimpleLogger logger, ShellScript sh, BooleanProperty isRunning) {
        this.cmdName = cmdName;
        this.btnStart = btn;
        this.logger = logger;
        this.sh = sh;
        this.isRunning = isRunning;
        this.exitcode = -1;
        this.resultString = "";
    }

    public AirtoolsCLICommand(String cmdName, Button btn, SimpleLogger logger, ShellScript sh) {
        this(cmdName, btn, logger, sh, new SimpleBooleanProperty(true));
    }

    public AirtoolsCLICommand(Button btn, SimpleLogger logger, ShellScript sh, BooleanProperty isRunning) {
        this("usercmd", btn, logger, sh, isRunning);
    }

    public AirtoolsCLICommand(Button btn, SimpleLogger logger, ShellScript sh) {
        this("usercmd", btn, logger, sh);
    }

    public void setCmdName(String cmdName) {
        this.cmdName = cmdName;
    }

    public void setOpts(String[] opts) {
        this.opts = opts;
    }

    public void setArgs(String[] args) {
        this.args = args;
    }
    
    public int getExitCode () {
        return exitcode;
    }
    
    public String getResultString () {
        return resultString;
    }
    
    public void run() {
        /* returns sh.getOutput() */
        final String labelStart;
        String colorStart = "#333333";
        String colorStop = "#f00000";
        String str;
        int i;
        
        if (task == null) {
            // ready for new task
            logger.log("");
            exitcode=-1;
            resultString="";
            isRunning.setValue(Boolean.TRUE);
            //logger.log("# " + "Running ds9cmd " + taskName + opts + args);
            logger.statusLog("Running " + cmdName + " ...");
            if (btnStart != null) {
                labelStart = btnStart.getText();
                btnStart.setText("Stop");
                btnStart.setStyle("-fx-text-fill: " + colorStop);
            } else {
                labelStart = "";
            }
            
            // convert opts array to optsStr
            str="";
            for (i=0; i<opts.length; i++) {
                 if (! str.isEmpty()) str = str + " ";
                 str = str + opts[i];
            }
            final String optsStr = str;
            //logger.log("argsStr=" + argsStr);
            
            // convert args array to argsStr
            str="";
            for (i=0; i<args.length; i++) {
                 if (! str.isEmpty()) str = str + " ";
                 str = str + args[i];
            }
            final String argsStr = str;
            //logger.log("argsStr=" + argsStr);
            
            task = new Task<Void>() {
                int exitCode=0;

                @Override
                protected Void call() {
                    sh.setEnvVars("");
                    sh.setOpts(optsStr);
                    sh.setArgs(argsStr);
                    //sh.runFunction("\"" + userCmd + "\"");
                    sh.runFunction(cmdName);
                    return null;
                }
            };
            task.setOnSucceeded(e -> {
                exitcode=sh.getExitCode();
                resultString=sh.getOutput();
                if (exitcode == 0) {
                    logger.statusLog("Task finished");
                } else {
                    logger.statusLog("Task failed");
                }
                task=null;
                if (btnStart != null) {
                    btnStart.setText(labelStart);
                    btnStart.setStyle("-fx-text-fill: " + colorStart);
                }
                isRunning.setValue(Boolean.FALSE);
            });
            task.setOnCancelled(e -> {
                exitcode=-1;
                logger.statusLog("Task cancelled");
                task=null;
                if (btnStart != null) {
                    btnStart.setText(labelStart);
                    btnStart.setStyle("-fx-text-fill: " + colorStart);
                }
                isRunning.setValue(Boolean.FALSE);
            });
            thread = new Thread(task);
            thread.setDaemon(true);
            thread.start();
        } else {
            // task is running, interrupt it
            try {
                int killExitCode = sh.killProcess();
                if (killExitCode != 0) {
                    logger.log("Failed to kill process");
                    logger.statusLog("Failed to kill process");
                } else {
                    task.cancel();
                }
            } catch (Exception ex) {
                logger.log(ex);
                logger.log("Failed to cancel task");
                logger.statusLog("Failed to cancel task");
            }
            exitcode=-1;
            isRunning.setValue(Boolean.FALSE);
        }
    }

    public void waitFor() {
        if (task != null && thread.isAlive()) try {
            thread.join();
        } catch (InterruptedException ex) {
            Logger.getLogger(AirtoolsCLICommand.class.getName()).log(Level.SEVERE, null, ex);
        }
    }
}
