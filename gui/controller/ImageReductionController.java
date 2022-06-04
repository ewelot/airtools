/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package tl.airtoolsgui.controller;

import tl.airtoolsgui.model.AirtoolsTask;
import tl.airtoolsgui.model.ShellScript;
import tl.airtoolsgui.model.SimpleLogger;

import java.net.URL;
import java.util.ArrayList;
import java.util.List;
import java.util.ResourceBundle;
import javafx.application.Platform;
import javafx.beans.value.ObservableValue;
import javafx.concurrent.Task;
import javafx.event.ActionEvent;
import javafx.fxml.FXML;
import javafx.fxml.Initializable;
import javafx.scene.control.Button;
import javafx.scene.control.CheckBox;
import javafx.scene.control.Label;
import javafx.scene.control.TextField;
import javafx.scene.image.ImageView;

/**
 * FXML Controller class
 *
 * @author lehmann
 */
public class ImageReductionController implements Initializable {

    @FXML
    private CheckBox cbImageinfo;
    @FXML
    private Label labelImageinfo;
    @FXML
    private CheckBox cbDarks;
    @FXML
    private Label labelDarks;
    @FXML
    private CheckBox cbFlats;
    @FXML
    private Label labelFlats;
    @FXML
    private CheckBox cbLights;
    @FXML
    private Label labelLights;
    @FXML
    private CheckBox cbBgvar;
    @FXML
    private Label labelBgvar;
    @FXML
    private CheckBox cbRegister;
    @FXML
    private Label labelRegister;
    @FXML
    private CheckBox cbStack;
    @FXML
    private Label labelStack;
    @FXML
    private CheckBox cbAstrometry;
    @FXML
    private Label labelAstrometry;
    @FXML
    private CheckBox cbCostack;
    @FXML
    private Label labelCostack;
    @FXML
    private TextField tfProgramOptions;
    @FXML
    private TextField tfImageSets;
    @FXML
    private CheckBox cbOverwrite;
    @FXML
    private Label labelWarning;
    @FXML
    private CheckBox cbProcessImages;
    @FXML
    private CheckBox cbViewPlots;
    @FXML
    private CheckBox cbShowImages;
    @FXML
    private Button buttonStart;

    private SimpleLogger logger;
    private ShellScript sh;

    private Task task;
    private final List<AirtoolsTask> taskList = new ArrayList<>();
    private boolean isFirstTask=true;

    final String colorStopBtn = "#f00000";
    final String colorNormalBtn = "#333333";

    /**
     * Initializes the controller class.
     */
    @Override
    public void initialize(URL url, ResourceBundle rb) {
        System.out.println("ImageReductionController: initialize");
        initAirtoolsTasks();
        ImageView icon = new ImageView("/tl/airtoolsgui/icons/warning.png");
        labelWarning.setText("");
        labelWarning.setGraphic(icon);

        labelWarning.setVisible(false);
        cbOverwrite.setSelected(false);
        
        cbOverwrite.selectedProperty().addListener(
            (ObservableValue<? extends Boolean> ov, Boolean oldValue, Boolean newValue) -> {
            labelWarning.setVisible(newValue);
        });
    }
    

    public void setReferences (ShellScript sh, SimpleLogger logger) {
        System.out.println("ImageReductionController: setReferences");
        this.sh = sh;
        this.logger = logger;
    }

    
    public void updateTabContent () {
        System.out.println("ImageReductionController: updateTabContent");
    }
    
    
    public void clearTabContent () {
        System.out.println("ImageReductionController: clearTabContent");
        tfImageSets.setText("");
        tfProgramOptions.setText("");
        cbImageinfo.setSelected(false);
        cbDarks.setSelected(false);
        cbFlats.setSelected(false);
        cbLights.setSelected(false);
        cbBgvar.setSelected(false);
        cbRegister.setSelected(false);
        cbStack.setSelected(false);
        cbAstrometry.setSelected(false);
        cbCostack.setSelected(false);
    }
    
    
    private void initAirtoolsTasks () {
        AirtoolsTask taskImageinfo = new AirtoolsTask(
                "imageinfo", cbImageinfo, labelImageinfo);
        taskList.add(taskImageinfo);
        
        AirtoolsTask taskDarks = new AirtoolsTask(
                "darks", cbDarks, labelDarks);
        taskList.add(taskDarks);
        
        AirtoolsTask taskFlats = new AirtoolsTask(
                "flats", cbFlats, labelFlats);
        taskList.add(taskFlats);
        
        AirtoolsTask taskLights = new AirtoolsTask(
                "lights", cbLights, labelLights);
        taskList.add(taskLights);
        
        AirtoolsTask taskBgvar = new AirtoolsTask(
                "bgvar", cbBgvar, labelBgvar);
        taskList.add(taskBgvar);
        
        AirtoolsTask taskRegister = new AirtoolsTask(
                "register", cbRegister, labelRegister);
        taskList.add(taskRegister);
        
        AirtoolsTask taskStack = new AirtoolsTask(
                "stack", cbStack, labelStack);
        taskList.add(taskStack);
        
        AirtoolsTask taskAstrometry = new AirtoolsTask(
                "astrometry", cbAstrometry, labelAstrometry);
        taskList.add(taskAstrometry);
        
        AirtoolsTask taskCostack = new AirtoolsTask(
                "costack", cbCostack, labelCostack);
        taskList.add(taskCostack);
    }
    
    
    @FXML
    private void onButtonStart(ActionEvent event) {
        Button btn = (Button) event.getSource();
        boolean hasSelectedTasks = false;
        if (task == null) {
            // ready for new task
            logger.log("");
            
            for (AirtoolsTask aTask : taskList) {
                if (aTask.isSelected()) hasSelectedTasks=true;
            }
            if (! hasSelectedTasks) {
                logger.log("# WARNING: there are no selected tasks");
            }
            logger.statusLog("Running selected tasks ...");
            btn.setText("Stop");
            btn.setStyle("-fx-text-fill: " + colorStopBtn);
            for (AirtoolsTask aTask : taskList) {
                aTask.setStatus("");
            }
            
            task = new Task<Void>() {
                String vars="";    // environment variables
                String opts="";    // command line options for shell script
                String args="";    // command line arguments for function
                int exitCode=0;
                int idx=0;
                @Override
                protected Void call() {
                    for (AirtoolsTask aTask : taskList) {
                        opts="";
                        String skipParts="";
                        if (isCancelled()) break;
                        if (!aTask.isSelected() || exitCode != 0) continue;
                        Platform.runLater(() -> {
                            aTask.setStatus("Running ...");
                        });
                        if (isFirstTask) {
                            isFirstTask = false;
                        } else {
                            opts+=" -q";
                        }
                        if (! tfProgramOptions.getText().isEmpty()) {
                            vars=tfProgramOptions.getText();
                        }
                        
                        // skip some program parts if requested
                        if (! cbProcessImages.isSelected() &&
                                ! cbViewPlots.isSelected() &&
                                ! cbShowImages.isSelected()) {
                            logger.log("# WARNING: processing skipped (all options deselected)");
                            break;
                        }
                        if (! cbProcessImages.isSelected()) {
                            skipParts+="proc";
                        }
                        if (! cbViewPlots.isSelected()) {
                            if (! skipParts.isEmpty()) skipParts+=",";
                            skipParts+="plot";
                        }
                        if (! cbShowImages.isSelected()) {
                            if (! skipParts.isEmpty()) skipParts+=",";
                            skipParts+="image";
                        }
                        if (! skipParts.isEmpty()) opts+=" -x " + skipParts;
                        
                        // delete previous results if requested
                        if (cbOverwrite.isSelected()) {
                            opts+=" -o";
                        }

                        // limit to given image sets if requested
                        if (! tfImageSets.getText().isEmpty()) {
                            opts+=" -s \"" + tfImageSets.getText() + "\"";
                        }
                        
                        sh.setEnvVars(vars);
                        sh.setOpts(opts);
                        sh.setArgs(args);
                        sh.runFunction(aTask.getFuncName());
                        exitCode=sh.getExitCode();
                        //logger.log("shell script finished with " + exitCode);
                        if (exitCode == 0) {
                            Platform.runLater(() -> {
                                aTask.setStatus("Done");
                                aTask.deSelect();
                            });
                        } else {
                            Platform.runLater(() -> {
                                aTask.setStatus("ERROR");
                            });
                        }
                        idx++;
                    }
                    return null;
                }
            };
            task.setOnSucceeded(e -> {
                if (sh.getExitCode() == 0) {
                    logger.statusLog("Tasks finished");
                } else {
                    logger.statusLog("Tasks failed");
                }
                task=null;
                btn.setText("Start");
                btn.setStyle("-fx-text-fill: " + colorNormalBtn);
            });
            task.setOnCancelled(e -> {
                logger.statusLog("Tasks cancelled");
                task=null;
                btn.setText("Start");
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
    
}
