/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package tl.airtoolsgui.controller;

import tl.airtoolsgui.model.ImageSet;
import tl.airtoolsgui.model.ShellScript;
import tl.airtoolsgui.model.SimpleLogger;
import java.io.BufferedReader;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.io.InputStreamReader;
import java.net.URL;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.ResourceBundle;
import java.util.stream.Stream;
import javafx.beans.property.SimpleStringProperty;
import javafx.beans.property.StringProperty;
import javafx.concurrent.Task;
import javafx.event.ActionEvent;
import javafx.fxml.FXML;
import javafx.fxml.Initializable;
import javafx.scene.control.Alert;
import javafx.scene.control.Button;
import javafx.scene.control.TextField;
import javafx.scene.input.KeyCode;

/**
 * FXML Controller class
 *
 * @author lehmann
 */
public class MiscToolsController implements Initializable {

    @FXML
    private Button buttonLoadRaws;
    @FXML
    private Button buttonLoadImages;
    @FXML
    private Button buttonAladin;
    @FXML
    private Button buttonFileManager;
    @FXML
    private Button buttonTerminal;
    @FXML
    private TextField tfLoadRawsArgs;
    @FXML
    private TextField tfLoadImagesArgs;
    @FXML
    private TextField tfAladinArgs;
    
    @FXML
    private TextField tfCommand;
    @FXML
    private Button buttonClearCommand;
    @FXML
    private Button buttonRunCommand;

    private SimpleLogger logger;
    private ShellScript sh;
    private Task task;
    public StringProperty projectDir = new SimpleStringProperty();
    private final List<ImageSet> imageSetList = new ArrayList<>();

    final String colorStopBtn = "#f00000";
    final String colorNormalBtn = "#333333";
    private String origText;

    /**
     * Initializes the controller class.
     */
    @Override
    public void initialize(URL url, ResourceBundle rb) {
        System.out.println("MiscToolsController: initialize");
        tfCommand.setOnKeyReleased(event -> {
            if (event.getCode() == KeyCode.ENTER){
                String userCmd = tfCommand.getText();
                if (! userCmd.isEmpty()) buttonRunCommand.fire();
            }
        });
    }    
    

    public void setReferences (ShellScript sh, SimpleLogger logger) {
        System.out.println("MiscToolsController: setReferences");
        this.sh = sh;
        this.logger = logger;
    }
    
    
    public void clearTabContent () {
        System.out.println("MiscToolsController: clearTabContent");
        tfLoadRawsArgs.setText("");
        tfLoadImagesArgs.setText("");
        tfAladinArgs.setText("");
        tfCommand.setText("");
    }
    
    
    public void showEnvironment () {
        String[] cmd;
        String output;
        String outfilename=System.getenv("HOME") + "/airtools_env.txt";
        
        cmd = new String[] {"bash", "-c", "env"};
        
        logger.log("");
        logger.log("# Current environment variables:");
        output=executeShellCommand(cmd, true);
        System.out.println(output);
        try {
            File newTextFile = new File(outfilename);

            FileWriter fw = new FileWriter(newTextFile);
            fw.write(output);
            fw.close();
            logger.log("");
            logger.log("# Last output has been copied to " + outfilename);

        } catch (IOException e) {
            //do stuff with exception
            e.printStackTrace();
        }
    }

    
    @FXML
    private void onButtonLoadRaws(ActionEvent event) {
        String args = tfLoadRawsArgs.getText();
        runAirtoolsCommand("imexa_raw", new String[] {args}, (Button) event.getSource());
    }

    @FXML
    private void onButtonLoadImages(ActionEvent event) {
        String args = tfLoadImagesArgs.getText();
        runAirtoolsCommand("imexa_calib", new String[] {args}, (Button) event.getSource());
    }

    @FXML
    private void onButtonAladin(ActionEvent event) {
        String[] args = Stream.of(
                new String[] {"AIaladin", "-a"},
                tfAladinArgs.getText().split("\\s+")).flatMap(Stream::of).toArray(String[]::new);
        runAirtoolsCommand("usercmd", args, (Button) event.getSource());
    }

    @FXML
    private void onButtonFileManager(ActionEvent event) {
        String[] cmd;
        cmd = new String[] {"xdg-open", projectDir.getValue()};
        System.out.println(executeShellCommand(cmd, false));
    }

    @FXML
    private void onButtonTerminal(ActionEvent event) {
        String[] args = {""};
        runAirtoolsCommand("terminal", args, (Button) event.getSource());
    }

    @FXML
    private void old_onButtonTerminal(ActionEvent event) {
        String[] cmd;
        cmd = new String[] {"x-terminal-emulator", "-e",
            "env PROMPT_COMMAND=\"unset PROMPT_COMMAND; cd " + projectDir.getValue() + ";"
                + ". .airtoolsrc;"
                + ". $(type -p airfun.sh)\" bash"};
        System.out.println(executeShellCommand(cmd, false));
    }
    

    @FXML
    private void onButtonClearCommand(ActionEvent event) {
        tfCommand.setText("");
    }

    @FXML
    private void onButtonRunCommand(ActionEvent event) {
        String userCmd = tfCommand.getText();
        if (! userCmd.isEmpty()) {
            String[] args = userCmd.split("\\s+");
            runAirtoolsCommand("usercmd", args, (Button) event.getSource());
        }
    }
    
    
    private void runAirtoolsCommand (String cmd, String[] args, Button btn) {
        if (task == null) {
            // ready for new task
            logger.log("");
            //logger.log("# " + "Running ds9cmd " + taskName + " " + args);
            logger.statusLog("Running " + cmd + " ...");
            origText = btn.getText();
            btn.setText("Stop");
            btn.setStyle("-fx-text-fill: " + colorStopBtn);
            
            // convert args to argsStr
            String str="";
            int i;
            for (i=0; i<args.length; i++) {
                 if (! str.isEmpty()) str = str + " ";
                 str = str + "\"" + args[i] + "\"";
            }
            final String argsStr = str;
            //logger.log("argsStr=" + argsStr);
            
            task = new Task<Void>() {
                int exitCode=0;

                @Override
                protected Void call() {
                    sh.setEnvVars("");
                    sh.setOpts("");
                    sh.setArgs(argsStr);
                    //sh.runFunction("\"" + userCmd + "\"");
                    sh.runFunction(cmd);
                    exitCode=sh.getExitCode();
                    //logger.log("shell script finished with " + exitCode);
                    return null;
                }
            };
            task.setOnSucceeded(e -> {
                if (sh.getExitCode() == 0) {
                    logger.statusLog("Task finished");
                } else {
                    logger.statusLog("Task failed");
                }
                task=null;
                btn.setText(origText);
                btn.setStyle("-fx-text-fill: " + colorNormalBtn);
            });
            task.setOnCancelled(e -> {
                logger.statusLog("Task cancelled");
                task=null;
                btn.setText(origText);
                btn.setStyle("-fx-text-fill: " + colorNormalBtn);
            });
            Thread thread = new Thread(task);
            thread.setDaemon(true);
            thread.start();
        } else {
            // task is running, interrupt it
            try {
                int exitCode = sh.killProcess();
                if (exitCode != 0) {
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
        } 
    }

    
    private String executeShellCommand(String command[], boolean doLog) {
        StringBuilder output = new StringBuilder();
        Process p;

        //System.out.println("# executeCommand: " + Arrays.toString(command));
        try {
            p = Runtime.getRuntime().exec(command);
            BufferedReader stdOutput = 
                new BufferedReader(new InputStreamReader(p.getInputStream()));
            BufferedReader stdError = 
                new BufferedReader(new InputStreamReader(p.getErrorStream()));
            String line;
            while ((line = stdOutput.readLine())!= null) {
                if (doLog) logger.log(line);
                output.append(line + "\n");
            }
            while ((line = stdError.readLine())!= null) {
                if (doLog) logger.log(line);
                output.append(line + "\n");
            }
            //p.waitFor();
        } catch (Exception e) {
            logger.log("ERROR: shell command failed: " + Arrays.toString(command));
            e.printStackTrace();
        }

        return output.toString();
    }
    
    private void showUnderConstructionDialog() {
        Alert alert = new Alert(Alert.AlertType.INFORMATION);
        alert.setTitle("Information");
        alert.setHeaderText("Sorry, ...");
        alert.setContentText("this action has not been implemented yet.");
        alert.setResizable(true);
        // TODO: increase size relative to system size
        //alert.getDialogPane().setStyle("-fx-font-size: 14px;");
        //alert.getDialogPane().getScene().getWindow().sizeToScene();
        alert.getDialogPane().setMinHeight(200);
        alert.showAndWait();
    }
}
