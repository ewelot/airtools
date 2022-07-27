/*
 * Click nbfs://nbhost/SystemFileSystem/Templates/Licenses/license-default.txt to change this license
 * Click nbfs://nbhost/SystemFileSystem/Templates/javafx/FXMLController.java to edit this template
 */
package tl.airtoolsgui.controller;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.IOException;
import java.net.URL;
import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.time.format.DateTimeParseException;
import java.util.ArrayList;
import java.util.List;
import java.util.ResourceBundle;
import java.util.logging.Level;
import java.util.logging.Logger;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import javafx.application.Platform;
import javafx.beans.property.BooleanProperty;
import javafx.beans.property.SimpleBooleanProperty;
import javafx.beans.property.SimpleStringProperty;
import javafx.beans.property.StringProperty;
import javafx.collections.FXCollections;
import javafx.event.ActionEvent;
import javafx.fxml.FXML;
import javafx.fxml.Initializable;
import javafx.scene.Node;
import javafx.scene.control.Button;
import javafx.scene.control.CheckBox;
import javafx.scene.control.ChoiceBox;
import javafx.scene.control.DatePicker;
import javafx.scene.control.Label;
import javafx.scene.control.Spinner;
import javafx.scene.control.SpinnerValueFactory;
import javafx.scene.control.TextField;
import javafx.scene.layout.AnchorPane;
import javafx.stage.FileChooser;
import javafx.stage.Stage;
import javafx.util.StringConverter;
import tl.airtoolsgui.model.AirtoolsCLICommand;
import tl.airtoolsgui.model.Camera;
import tl.airtoolsgui.model.ShellScript;
import tl.airtoolsgui.model.SimpleLogger;

/**
 * FXML Controller class
 *
 * @author lehmann
 */
public class ImportFitsStacksController implements Initializable {

    @FXML
    private AnchorPane paneImportFitsStacks;
    @FXML
    private TextField tfImageSet;
    @FXML
    private TextField tfObject;
    @FXML
    private TextField tfStarStack;
    @FXML
    private Button buttonBrowseStarStack;
    @FXML
    private TextField tfCometStack;
    @FXML
    private Button buttonBrowseCometStack;
    @FXML
    private TextField tfExptime;
    @FXML
    private Spinner<Integer> spNExp;
    @FXML
    private Spinner<Integer> spNRef;
    @FXML
    private ChoiceBox<Camera> cbTelID;
    @FXML
    private DatePicker dpRefDate;
    @FXML
    private TextField tfRefTime;
    @FXML
    private CheckBox cbFlip;
    @FXML
    private CheckBox cbShow;
    @FXML
    private TextField tfExpert;
    @FXML
    private CheckBox cbDelete;
    @FXML
    private Label labelWarning;
    @FXML
    private Button buttonExamineFitsStacks;
    @FXML
    private Button buttonStart;
    @FXML
    private Button buttonCancel;
    
    private SimpleLogger logger;
    private StringProperty projectDir = new SimpleStringProperty();
    private StringProperty tempDir = new SimpleStringProperty();
    private AirtoolsCLICommand aircliCmd;
    private BooleanProperty cmdIsRunning = new SimpleBooleanProperty();
    private ShellScript sh;
    private final String aircliTask = "usercmd";
    private final String airfunFunc = "AIimport";

    private final List<Camera> cameraList = new ArrayList<>();
    private final DateTimeFormatter dateFormatter = 
        DateTimeFormatter.ofPattern("yyyy-MM-dd");
    private final Camera UNKNOWN_CAMERA = new Camera("unknown");

    
    /**
     * Initializes the controller class.
     */
    @Override
    public void initialize(URL url, ResourceBundle rb) {
        // TODO
        labelWarning.setText("");

        // add spinner ranges
        spNExp.setValueFactory(new SpinnerValueFactory.IntegerSpinnerValueFactory(1, 200, 1));
        spNRef.setValueFactory(new SpinnerValueFactory.IntegerSpinnerValueFactory(1, 200, 1));
        // note: editable spinner would requires extra handling of up/down keys via spNExp.getEditor().setOnKeyPressed

        // right align file names after leaving widget
        /* TODO: does not work properly, if another textfield gets focus the alignment
            changes and path appears left aligned again
        */
        /*
        tfStarStack.focusedProperty().addListener((c, oldValue, newValue) -> {
            if (newValue) {
                System.out.println("# tfStarStack focused");
            } else {
                System.out.println("# tfStarStack unfocused");
            }
            Platform.runLater(() -> {
                tfStarStack.deselect();
                tfStarStack.end();
            });
        });
        tfCometStack.focusedProperty().addListener((c, oldValue, newValue) -> {
            Platform.runLater(() -> {
                tfCometStack.deselect();
                tfCometStack.end();
            });
        });
        */
   
        // use custom format with all DatePickers
        dpRefDate.setConverter(new StringConverter<LocalDate>() {
            @Override 
            public String toString(LocalDate date) {
                if (date != null) {
                    return dateFormatter.format(date);
                } else {
                    return "";
                }
            }

            @Override 
            public LocalDate fromString(String string) {
                if (string != null && !string.isEmpty()) {
                    return LocalDate.parse(string, dateFormatter);
                } else {
                    return null;
                }
            }
        });
    }    

    public void setReferences (ShellScript sh, SimpleLogger logger, StringProperty projectDir, StringProperty tempDir) {
        this.logger = logger;
        this.projectDir = projectDir;
        this.aircliCmd = new AirtoolsCLICommand(buttonStart, logger, sh, cmdIsRunning);
        this.sh = sh;
        this.tempDir = tempDir;
        
        setCameraList();
        cbTelID.setItems(FXCollections.observableArrayList(
            cameraList));
        cbTelID.getSelectionModel().selectFirst();
        
        cmdIsRunning.addListener((obs, oldValue, newValue) -> {
            if (! newValue) {
                int exitCode = aircliCmd.getExitCode();
                System.out.println("command has finished with exit code " + exitCode);
                if (aircliCmd.getExitCode() != 0)
                    labelWarning.setText(aircliCmd.getResultString());
            }
        });

        paneImportFitsStacks.setOnMouseClicked(event -> {
            labelWarning.setText("");
        });
    }

    public void updateCameras () {
        setCameraList();
        cbTelID.getItems().clear();
        cbTelID.getItems().addAll(cameraList);
        cbTelID.getSelectionModel().selectFirst();
    }
    
    
    private void setCameraList () {
        System.out.println("ImportFitsStackController: setCameraList");
        BufferedReader inFile = null;
        try {
            inFile = new BufferedReader(new FileReader(projectDir.getValue() + "/camera.dat"));
            String line;
            Pattern regexp = Pattern.compile("^[a-zA-Z0-9]+[ ]+[0-9]+[ ]+[0-9]+[ ]+");
            Matcher matcher = regexp.matcher("");
            cameraList.clear();
            cameraList.add(new Camera("unknown"));
            try {
                while (( line = inFile.readLine()) != null){
                    matcher.reset(line);
                    if (matcher.find()) {
                        String[] columns = line.split("[ ]+");
                        if (columns.length >= 15) {
                            System.out.println(line);
                            cameraList.add(new Camera(columns[0], Integer.parseInt(columns[1]), Integer.parseInt(columns[2]), columns[4]));
                        }
                    }
                }
            } catch (IOException ex) {
                Logger.getLogger(ImportFitsStacksController.class.getName()).log(Level.SEVERE, null, ex);
            }
        } catch (FileNotFoundException ex) {
            Logger.getLogger(ImportFitsStacksController.class.getName()).log(Level.SEVERE, null, ex);
        } finally {
            try {
                inFile.close();
            } catch (IOException ex) {
                Logger.getLogger(ImportFitsStacksController.class.getName()).log(Level.SEVERE, null, ex);
            }
        }
    }
    
    
    @FXML
    private void onButtonBrowseStarStack(ActionEvent event) {
        FileChooser fileChooser = new FileChooser();
        String fileName = tfStarStack.getText();
        File pdir = new File(projectDir.getValue());
        
        if (fileName.isEmpty()) {
            fileChooser.setInitialDirectory(pdir);
        } else {
            File f = new File(fileName);
            fileChooser.setInitialDirectory(f.getParentFile());
            fileChooser.setInitialFileName(fileName);
        }
        fileChooser.getExtensionFilters().addAll(
            new FileChooser.ExtensionFilter("FITS Files", "*.fits", "*.fts", "*.fit")
        );

        Stage stage = (Stage) paneImportFitsStacks.getScene().getWindow();
        File selectedFile = fileChooser.showOpenDialog(stage);
        if (selectedFile != null) {
            String fullName = selectedFile.getAbsolutePath();
            if (fullName.startsWith(projectDir.getValue())) {
                tfStarStack.setText(fullName.substring(projectDir.getValue().length()+1));
            } else {
                tfStarStack.setText(selectedFile.getAbsolutePath());
                tfStarStack.end();
            }
        }
    }

    @FXML
    private void onButtonBrowseCometStack(ActionEvent event) {
         FileChooser fileChooser = new FileChooser();
        String fileName = tfCometStack.getText();
        File pdir = new File(projectDir.getValue());
        
        if (fileName.isEmpty()) {
            fileChooser.setInitialDirectory(pdir);
        } else {
            File f = new File(fileName);
            fileChooser.setInitialDirectory(f.getParentFile());
            fileChooser.setInitialFileName(fileName);
        }
        fileChooser.getExtensionFilters().addAll(
            new FileChooser.ExtensionFilter("FITS Files", "*.fits", "*.fts", "*.fit")
        );

        Stage stage = (Stage) paneImportFitsStacks.getScene().getWindow();
        File selectedFile = fileChooser.showOpenDialog(stage);
        if (selectedFile != null) {
            String fullName = selectedFile.getAbsolutePath();
            if (fullName.startsWith(projectDir.getValue())) {
                tfCometStack.setText(fullName.substring(projectDir.getValue().length()+1));
            } else {
                tfCometStack.setText(selectedFile.getAbsolutePath());
                tfCometStack.end();
            }
        }
    }

    @FXML
    private void onButtonExamineFitsStacks(ActionEvent event) {
        System.out.println("ImportFitsStackController: onButtonExamineFitsStacks()");
        if (tfStarStack.getText().isBlank() && tfCometStack.getText().isBlank()) return;
        
        labelWarning.setText("");
        AirtoolsCLICommand aUserCmd = new AirtoolsCLICommand((Button) event.getSource(), logger, sh);
        List<String> aircliCmdOpts = new ArrayList<>();
        List<String> aircliCmdArgs = new ArrayList<>();
        aircliCmdArgs.add("AIexamine");
        if (! tfStarStack.getText().isBlank()) aircliCmdArgs.add(tfStarStack.getText());
        if (! tfCometStack.getText().isBlank()) aircliCmdArgs.add(tfCometStack.getText());
        aUserCmd.setOpts(aircliCmdOpts.toArray(String[]::new));
        aUserCmd.setArgs(aircliCmdArgs.toArray(String[]::new));
        aUserCmd.run();
    }

    private boolean isValidInputs() {
        String msg="";
        LocalDate ld;
        if (tfImageSet.getText().isBlank()) {
            msg="ERROR: missing entry for image set.";
            labelWarning.setText(msg);
            logger.log(msg);
            return false;
        }
        if (tfObject.getText().isBlank()) {
            msg="ERROR: missing entry for object.";
            labelWarning.setText(msg);
            logger.log(msg);
            return false;
        }
        if (tfStarStack.getText().isBlank()) {
            msg="ERROR: no star stack selected.";
            labelWarning.setText(msg);
            logger.log(msg);
            return false;
        }
        if (cbTelID.getSelectionModel().getSelectedItem().equals(UNKNOWN_CAMERA)) {
            msg="ERROR: no camera selected.";
            labelWarning.setText(msg);
            logger.log(msg);
            return false;
        }
        if (tfExptime.getText().isBlank()) {
            msg="ERROR: missing entry for exposure time.";
            labelWarning.setText(msg);
            logger.log(msg);
            return false;
        }
        // TODO: check exptime is a positive integer/float
        if (spNRef.getValue() > spNExp.getValue()) {
            msg="ERROR: number of reference image is above number of exposures.";
        }
        if (dpRefDate.getEditor().getText().isBlank()) {
            msg="ERROR: missing start date of reference image.";
            labelWarning.setText(msg);
            logger.log(msg);
            return false;
        } else {
            try {
                ld=dpRefDate.getConverter().fromString(dpRefDate.getEditor().getText());
                dpRefDate.setValue(ld);
            } catch (DateTimeParseException ex) {
                msg="ERROR: entered string of start date does not match date format.";
                labelWarning.setText(msg);
                logger.log(msg);
                return false;
            }
        }
        if (tfRefTime.getText().isBlank()) {
            msg="ERROR: missing start time of reference image.";
            labelWarning.setText(msg);
            logger.log(msg);
            return false;
        }
        return true;
    }
    
    
    @FXML
    private void onButtonStart(ActionEvent event) {
        System.out.println("ImportFitsStacksController: onButtonStart()");
        labelWarning.setText("");
        List<String> aircliCmdOpts = new ArrayList<>();
        List<String> aircliCmdArgs = new ArrayList<>();

        if (! isValidInputs()) return;
        
        //FitType fitType=cbFitType.getSelectionModel().getSelectedItem();

        // airfun function to call
        aircliCmdArgs.add(airfunFunc);
        
        // add command options
        if (cbDelete.isSelected())aircliCmdArgs.add("-o");
        if (cbFlip.isSelected())aircliCmdArgs.add("-f");
        if (cbShow.isSelected())aircliCmdArgs.add("-s");
        
        if (! tfExpert.getText().isBlank()) {
            aircliCmdArgs.add(tfExpert.getText());
        }

        // add mandatory positional parameters
        aircliCmdArgs.add(tfImageSet.getText().toLowerCase());
        aircliCmdArgs.add(tfObject.getText());
        aircliCmdArgs.add(tfStarStack.getText());
        if (! tfCometStack.getText().isBlank()) {
            aircliCmdArgs.add(tfCometStack.getText());
        } else {
            aircliCmdArgs.add("\"\"");
        }
        aircliCmdArgs.add(cbTelID.getSelectionModel().getSelectedItem().getTelID());
        aircliCmdArgs.add(tfExptime.getText());
        aircliCmdArgs.add(Integer.toString(spNExp.getValue()));
        aircliCmdArgs.add(Integer.toString(spNRef.getValue()));
        aircliCmdArgs.add(dpRefDate.getValue() + "T" + tfRefTime.getText());
        /*
        if (! tfMagLim.getText().isBlank()) {
            aircliCmdArgs.add(tfMagLim.getText());
        } else {
            aircliCmdArgs.add("\"\"");
        }
        */

        // run command
        System.out.println("cmd: " + aircliCmdOpts + " " + aircliTask + " " + aircliCmdArgs);
        //logger.log("# cmd: " + aircliCmdOpts + " " + aircliTask + " " + aircliCmdArgs);
        aircliCmd.setOpts(aircliCmdOpts.toArray(String[]::new));
        aircliCmd.setArgs(aircliCmdArgs.toArray(String[]::new));
        aircliCmd.run();
        
        // TODO: run command after aircliCmd has finished
        //setButtonCOBSDataDisabledState();
    }

    @FXML
    private void onButtonCancel(ActionEvent event) {
        Node  source = (Node)  event.getSource(); 
        Stage stage  = (Stage) source.getScene().getWindow();
        stage.close();
    }
    
}
