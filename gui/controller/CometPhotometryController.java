/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package tl.airtoolsgui.controller;

import tl.airtoolsgui.model.PSFExtractDialog;
import tl.airtoolsgui.model.ImageSet;
import tl.airtoolsgui.model.ShellScript;
import tl.airtoolsgui.model.SimpleLogger;
import java.io.BufferedReader;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.FilenameFilter;
import java.io.IOException;
import java.net.URL;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Optional;
import java.util.ResourceBundle;
import java.util.logging.Level;
import java.util.logging.Logger;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import javafx.beans.property.SimpleStringProperty;
import javafx.beans.property.StringProperty;
import javafx.collections.FXCollections;
import javafx.concurrent.Task;
import javafx.event.ActionEvent;
import javafx.fxml.FXML;
import javafx.fxml.Initializable;
import javafx.scene.control.Alert;
import javafx.scene.control.Button;
import javafx.scene.control.ButtonType;
import javafx.scene.control.ChoiceBox;
import tl.airtoolsgui.model.BgGradientDialog;
import tl.airtoolsgui.model.CometExtractDialog;
import tl.airtoolsgui.model.ManualDataDialog;
import tl.airtoolsgui.model.PhotometryDialog;

/**
 * FXML Controller class
 *
 * @author lehmann
 */
public class CometPhotometryController implements Initializable {

    @FXML
    private ChoiceBox<ImageSet> cbImageSet;

    @FXML
    private Button buttonRunLoadImages;
    @FXML
    private Button buttonRunBggradient;
    @FXML
    private Button buttonRunPsfextract;
    @FXML
    private Button buttonRunCometextract;
    @FXML
    private Button buttonRunManualdata;
    @FXML
    private Button buttonRunPhotometry;

    // dialogs
    private BgGradientDialog bggradientDialog = null;
    private PSFExtractDialog psfextractDialog = null;
    private CometExtractDialog cometextractDialog = null;
    private ManualDataDialog manualdataDialog = null;
    private PhotometryDialog photometryDialog = null;

    private SimpleLogger logger;
    private ShellScript sh;
    private Task task;
    public StringProperty projectDir = new SimpleStringProperty();
    private final List<ImageSet> imageSetList = new ArrayList<>();

    final String colorStopBtn = "#f00000";
    final String colorNormalBtn = "#333333";

    /**
     * Initializes the controller class.
     */
    @Override
    public void initialize(URL url, ResourceBundle rb) {
        System.out.println("CometPhotometryController: initialize");
        cbImageSet.getSelectionModel().selectedItemProperty().addListener((v, oldValue, newValue) -> {
            System.out.println("selected set: " + newValue);
        });
    }    
    

    public void setReferences (ShellScript sh, SimpleLogger logger) {
        System.out.println("CometPhotometryController: setReferences");
        this.sh = sh;
        this.logger = logger;
    }

    
    public void clearTabContent () {
        System.out.println("CometPhotometryController: clearTabContent");
        imageSetList.clear();
        cbImageSet.getItems().clear();
        clearDialogs();
    }
    
    
    public void updateTabContent () {
        // called by from project change or tab switch
        System.out.println("CometPhotometryController: updateTabContent");
        File inFile = new File(projectDir.getValue() + "/set.dat");
        if (inFile.exists() && inFile.isFile()) {
            final List<ImageSet> oldImageSetList = new ArrayList<>(imageSetList);
            setImageSetList();
            if (! imageSetList.equals(oldImageSetList)) {
                populateChoiceBoxImageSet();
            
                // TODO: try to keep originally selected ImageSet
                // TODO: if selected ImageSet differs from old one then run
                cbImageSet.getSelectionModel().selectFirst();
                clearDialogs();
            }
        } else {
            clearTabContent();
        }
    }
    

    public boolean hasImageSets () {
        return imageSetList != null && imageSetList.size() > 0;
    }
    
    
    private void clearDialogs() {
        System.out.println("CometPhotometryController: clearDialogs");
        // reset dialogs to initial state
        if (bggradientDialog != null)   bggradientDialog.setImageSet(null);
        if (psfextractDialog != null)   psfextractDialog.setImageSet(null);
        if (cometextractDialog != null) cometextractDialog.setImageSet(null);
        if (manualdataDialog != null)   manualdataDialog.setImageSet(null);
        if (photometryDialog != null)   photometryDialog.setImageSet(null);        
    }
    
    
    private void populateChoiceBoxImageSet() {
        System.out.println("populateChoiceBoxImageSet()");
        cbImageSet.setItems(FXCollections.observableArrayList(
            imageSetList));
    }

    
    private void setImageSetList () {
        System.out.println("setImageSetList");
        BufferedReader inFile = null;
        try {
            inFile = new BufferedReader(new FileReader(projectDir.getValue() + "/set.dat"));
            String line;
            // lights only: grep -E "^[0-9]{2}:[0-9]{2}[ ]+[a-zA-Z0-9]+[ ]+[a-zA-Z0-9-]+[ ]+[o][ ]+" set.dat
            Pattern regexp = Pattern.compile("^[0-9]{2}:[0-9]{2}[ ]+[a-zA-Z0-9]+[ ]+[a-zA-Z0-9-]+[ ]+[o][ ]+");
            Matcher matcher = regexp.matcher("");
            imageSetList.clear();
            try {
                while (( line = inFile.readLine()) != null){
                    matcher.reset(line);
                    if (matcher.find()) {
                        String[] columns = line.split("[ ]+");
                        if (columns.length >= 11) {
                            // Note: does require telid in field 11
                            System.out.println(line);
                            imageSetList.add(new ImageSet(projectDir.getValue(), columns[1], columns[2], 1));
                        }
                    }
                }
            } catch (IOException ex) {
                Logger.getLogger(CometPhotometryController.class.getName()).log(Level.SEVERE, null, ex);
            }
        } catch (FileNotFoundException ex) {
            Logger.getLogger(CometPhotometryController.class.getName()).log(Level.SEVERE, null, ex);
        } finally {
            try {
                inFile.close();
            } catch (IOException ex) {
                Logger.getLogger(CometPhotometryController.class.getName()).log(Level.SEVERE, null, ex);
            }
        }
    }
    
    

    @FXML
    private void onButtonRunLoadImages(ActionEvent event) {
        System.out.println("onButtonLoadImages()");
        Button btn = (Button) event.getSource();
        String btnText = btn.getText();
        if (task == null) {
            // ready for new task
            logger.log("");
            logger.log("# " + btnText + " ...");
            logger.statusLog("Running task load_stacks ...");
            btn.setText("Stop " + btnText);
            btn.setStyle("-fx-text-fill: " + colorStopBtn);
            
            task = new Task<Void>() {
                int exitCode=0;

                @Override
                protected Void call() {
                    String setname = cbImageSet.getSelectionModel().getSelectedItem().getSetname();
                    sh.setOpts("-s " + setname);
                    sh.setArgs("");
                    sh.runFunction("load_stacks");
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
                btn.setText(btnText);
                btn.setStyle("-fx-text-fill: " + colorNormalBtn);
            });
            task.setOnCancelled(e -> {
                logger.statusLog("Task cancelled");
                task=null;
                btn.setText(btnText);
                btn.setStyle("-fx-text-fill: " + colorNormalBtn);
            });
            Thread thread = new Thread(task);
            thread.setDaemon(true);
            thread.start();
        } else {
            // task is running, interrupt is
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

    
    @FXML
    private void onButtonRunBggradient(ActionEvent event) {
        System.out.println("onButtonRunBggradient()");
        String[] defaultParams = {"64", "plane", "10"};
        if (! isReady()) return;
        
        // show additional user instructions
        //logger.log("--> Note: any regions drawn on the comet stack image will be excluded from the background fit");
        
        ImageSet imgSet = cbImageSet.getSelectionModel().getSelectedItem();
        if (bggradientDialog == null) {
            bggradientDialog = new BgGradientDialog("BgGradient.fxml", "Background Gradient");
        }
        if (bggradientDialog.isNewImageSet(imgSet)) {
            bggradientDialog.setImageSet(imgSet);
            bggradientDialog.setValues(defaultParams);
        }

        Optional<ButtonType> result = bggradientDialog.run();
        if (result.isPresent() && result.get() == ButtonType.APPLY) {
            String[] taskParam = bggradientDialog.getValues();
            System.out.println("Parameters: " + Arrays.toString(taskParam));
            runDs9Command("bggradient", taskParam, (Button) event.getSource());
        }
    }


    @FXML
    private void onButtonRunPsfextract(ActionEvent event) {
        System.out.println("onButtonRunPsfextract()");
        String[] defaultParams = {"10", "0.2", "80"};
        if (! isReady()) return;
        ImageSet imgSet = cbImageSet.getSelectionModel().getSelectedItem();
        if (psfextractDialog == null) {
            psfextractDialog = new PSFExtractDialog("PSFExtract.fxml", "PSF Extraction");
        }
        if (psfextractDialog.isNewImageSet(imgSet)) {
            psfextractDialog.setImageSet(imgSet);
            psfextractDialog.setValues(defaultParams);
        }

        Optional<ButtonType> result = psfextractDialog.run();
        if (result.isPresent() && result.get() == ButtonType.APPLY) {
            String[] taskParam = psfextractDialog.getValues();
            System.out.println("Task Parameters: " + Arrays.toString(taskParam));
            runDs9Command("psfextract", taskParam, (Button) event.getSource());
        }
    }
    
    
    @FXML
    private void onButtonRunCometextract(ActionEvent event) {
        System.out.println("onButtonRunCometextract()");
        if (! isReady()) return;
        ImageSet imgSet = cbImageSet.getSelectionModel().getSelectedItem();
        String ext = "pgm";
        String bgImage="";
        if (imgSet.getStarStack().endsWith(".ppm")) ext="ppm";
        
        // choose the latest bgcorr image (bgm10 or bgm1)
        final String patternStr = imgSet.getSetname() + ".bgm[0-9]+." + ext
                + "|" + imgSet.getSetname() + ".bgm[0-9]+all." + ext;
        System.out.println("# pattern = " + patternStr);
        File bgcorrDir = new File(projectDir.getValue() + "/bgcorr");
        if (bgcorrDir.exists()) {
            File[] matchedFiles=bgcorrDir.listFiles(new FilenameFilter() {
                    final private Pattern pattern = Pattern.compile(patternStr);

                    @Override
                    public boolean accept(File dir, String name) {
                        return pattern.matcher(new File(name).getName()).matches();
                    }
                });
            if (matchedFiles.length > 0) {
                //logger.log("# number of matched files = " + matchedFiles.length);
                File mostRecentBgImage = Arrays
                    .stream(matchedFiles)
                    .filter(f -> f.isFile())
                    .max(
                        (f1, f2) -> Long.compare(f1.lastModified(),
                            f2.lastModified())).get();

                if (mostRecentBgImage.exists())
                    bgImage = "bgcorr/" + mostRecentBgImage.getName();
            }
        }
        String[] defaultParams = {bgImage, "10", "100"};

        if (cometextractDialog == null) {
            cometextractDialog = new CometExtractDialog("CometExtract.fxml", "Comet Extraction");
        }
        if (cometextractDialog.isNewImageSet(imgSet)) {
            cometextractDialog.setImageSet(imgSet);
            cometextractDialog.setValues(defaultParams);
        }

        Optional<ButtonType> result = cometextractDialog.run();
        if (result.isPresent() && result.get() == ButtonType.APPLY) {
            String[] taskParam = cometextractDialog.getValues();
            System.out.println("Task Parameters: " + Arrays.toString(taskParam));
            runDs9Command("cometextract", taskParam, (Button) event.getSource());
        }
    }

    
    @FXML
    private void onButtonRunManualdata(ActionEvent event) {
        System.out.println("onButtonRunManualdata()");
        if (! isReady()) return;
        ImageSet imgSet = cbImageSet.getSelectionModel().getSelectedItem();
        String channel = "1";
        if (imgSet.getStarStack().endsWith(".ppm")) channel="2";
        String[] defaultParams = {channel, "", "", "", "", "", ""};

        if (manualdataDialog == null) {
            manualdataDialog = new ManualDataDialog("ManualData.fxml", "Manual Measurements");
        }
        if (manualdataDialog.isNewImageSet(imgSet)) {
            manualdataDialog.setImageSet(imgSet);
            manualdataDialog.setValues(defaultParams);
        }

        Optional<ButtonType> result = manualdataDialog.run();
        if (result.isPresent() && result.get() == ButtonType.APPLY) {
            String[] taskParam = manualdataDialog.getValues();
            System.out.println("Task Parameters: " + Arrays.toString(taskParam));
            runDs9Command("manualdata", taskParam, (Button) event.getSource());
        }
    }

    
    @FXML
    private void onButtonRunPhotometry(ActionEvent event) {
        System.out.println("onButtonRunPhotometry()");
        if (! isReady()) return;
        ImageSet imgSet = cbImageSet.getSelectionModel().getSelectedItem();
        String plane = "1";
        if (imgSet.getStarStack().endsWith(".ppm")) plane="2";
        String refcat = "APASS";
        String color = "V+c(B-V)";
        String aprad = "";
        String ty2Opts = "-l 12.5";
        String apassOpts = "-n 200";
        String skip="";
        String[] defaultParams = {plane, refcat, color, aprad, ty2Opts, apassOpts, skip};

        if (photometryDialog == null) {
            photometryDialog = new PhotometryDialog("Photometry.fxml","Photometric Calibration");
        }
        if (photometryDialog.isNewImageSet(imgSet)) {
            photometryDialog.setImageSet(imgSet);
            photometryDialog.setValues(defaultParams);
        }

        Optional<ButtonType> result = photometryDialog.run();
        if (result.isPresent() && result.get() == ButtonType.APPLY) {
            String[] taskParam = photometryDialog.getValues();
            System.out.println("Task Parameters: " + Arrays.toString(taskParam));
            runDs9Command("photcal", taskParam, (Button) event.getSource());
        }
    }

    private boolean isReady() {
        System.out.println("running isReady()");
        ImageSet imgSet = cbImageSet.getSelectionModel().getSelectedItem();
        if (imgSet == null) {
            logger.log("ERROR: image set not defined");
            return false;
        }
        String starstack = imgSet.getStarStack();
        if (starstack == null || starstack.isEmpty()) {
            logger.log("ERROR: unable to find star stack for image set " + imgSet.getSetname());
            return false;
        }
        if (task != null) {
            System.out.println("calling sh.killProcess()");
            //task.cancel();
            sh.killProcess();
            return false;
        }
        return true;
    }


    private void runDs9Command (String taskName, String[] taskParams, Button btn) {
        System.out.println("runDs9Command(" + taskName + ", ...)");
        String str="";
        ImageSet imgSet = cbImageSet.getSelectionModel().getSelectedItem();
        
        if (taskName.equalsIgnoreCase("bggradient")) str=imgSet.getStarStack();
        if (taskName.equalsIgnoreCase("psfextract")) str=imgSet.getSetname() + " " + imgSet.getStarStack();
        if (taskName.equalsIgnoreCase("cometextract")) str=imgSet.getSetname() + " " + imgSet.getStarStack();
        if (taskName.equalsIgnoreCase("manualdata")) str=imgSet.getSetname();
        if (taskName.equalsIgnoreCase("photcal")) str=imgSet.getSetname();
        
        int i;
        for (i=0; i<taskParams.length; i++) {
             if (! str.isEmpty()) str = str + " ";
             str = str + "\"" + taskParams[i] + "\"";
        }
        final String args = str;

        if (task == null) {
            // ready for new task
            logger.log("");
            logger.log("# " + "Running ds9cmd " + taskName + " " + args);
            logger.statusLog("Running task " + taskName + " ...");
            btn.setText("Stop " + btn.getText());
            btn.setStyle("-fx-text-fill: " + colorStopBtn);
            //btn.getScene().setCursor(Cursor.WAIT);
            
            task = new Task<Void>() {
                int exitCode=0;

                @Override
                protected Void call() {
                    String setname = cbImageSet.getSelectionModel().getSelectedItem().getSetname();
                    sh.setEnvVars("");
                    sh.setOpts("");
                    sh.setArgs(taskName + " " + args);
                    sh.runFunction("ds9cmd");
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
                btn.setText(btn.getText().substring(5));
                btn.setStyle("-fx-text-fill: " + colorNormalBtn);
                //btn.getScene().setCursor(Cursor.DEFAULT);
            });
            task.setOnCancelled(e -> {
                logger.statusLog("Task cancelled");
                task=null;
                btn.setText(btn.getText().substring(5));
                btn.setStyle("-fx-text-fill: " + colorNormalBtn);
                //btn.getScene().setCursor(Cursor.DEFAULT);
            });
            Thread thread = new Thread(task);
            thread.setDaemon(true);
            thread.start();
        } else {
            // task is running, interrupt is
            logger.log("interrupting process" + sh.getPID());
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

    
    private void showUnderConstructionDialog() {
        Alert alert = new Alert(Alert.AlertType.INFORMATION);
        alert.setTitle("Information");
        alert.setHeaderText("Sorry, ...");
        alert.setContentText("this action has not been implemented yet.");
        alert.setResizable(true);
        alert.getDialogPane().setMinHeight(200);
        alert.showAndWait();
    }

}
