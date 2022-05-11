/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package tl.airtoolsgui.controller;

import java.io.File;
import java.io.IOException;
import java.net.URL;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.nio.file.StandardCopyOption;
import java.text.DateFormat;
import java.text.SimpleDateFormat;
import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.time.format.DateTimeParseException;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;
import java.util.ResourceBundle;
import java.util.logging.Level;
import java.util.logging.Logger;
import javafx.beans.property.SimpleStringProperty;
import javafx.beans.property.StringProperty;
import javafx.event.ActionEvent;
import javafx.fxml.FXML;
import javafx.fxml.Initializable;
import javafx.scene.Node;
import javafx.scene.control.Button;
import javafx.scene.control.CheckBox;
import javafx.scene.control.ChoiceBox;
import javafx.scene.control.DatePicker;
import javafx.scene.control.Label;
import javafx.scene.control.TextField;
import javafx.scene.layout.AnchorPane;
import javafx.stage.FileChooser;
import javafx.stage.Stage;
import tl.airtoolsgui.model.AirtoolsCLICommand;
import tl.airtoolsgui.model.ShellScript;
import tl.airtoolsgui.model.SimpleLogger;

/**
 * FXML Controller class
 *
 * @author lehmann
 */
public class LightCurveController implements Initializable {

    @FXML
    private AnchorPane paneLightCurve;
    @FXML
    private TextField tfCometName;
    @FXML
    private TextField tfICQFile;
    @FXML
    private Button buttonBrowseICQFile;
    @FXML
    private CheckBox cbUseCOBS;
    @FXML
    private CheckBox cbScanLocalProjects;
    @FXML
    private CheckBox cbForceUpdate;
    @FXML
    private ChoiceBox<PlotType> cbPlotType;
    @FXML
    private DatePicker dpStart;
    @FXML
    private DatePicker dpEnd;
    @FXML
    private TextField tfObsList;
    @FXML
    private ChoiceBox<KeyPosition> cbKeyPosition;
    @FXML
    private TextField tfAddOptions;
    @FXML
    private ChoiceBox<FitType> cbFitType;
    @FXML
    private CheckBox cbCurrentApparition;
    @FXML
    private TextField tfModelM;
    @FXML
    private TextField tfModelN;
    @FXML
    private CheckBox cbMPCModel;
    @FXML
    private CheckBox cbDistance;
    @FXML
    private Label labelWarning;
    
    @FXML
    private Button buttonCOBSData;
    @FXML
    private Button buttonStart;
    @FXML
    private Button buttonCancel;

    private SimpleLogger logger;
    private StringProperty projectDir = new SimpleStringProperty();
    private StringProperty tempDir = new SimpleStringProperty();
    private AirtoolsCLICommand aircliCmd;
    private final String aircliTask = "usercmd";
    private final String airfunFunc = "icqplot";

    
    private enum PlotType {
        MAG("Observed Magnitude"),
        HMAG("Heliocentric Magnitude vs. Date"),
        HMAGDIST("Heliocentric Magnitude vs. Distance"),
        COMA("Apparent Coma Diameter"),
        LCOMA("Linear Coma Diameter vs. Date"),
        LCOMADIST("Linear Coma Diameter vs. Distance");

        private final String label;

        PlotType(String label) {
            this.label = label;
        }

        @Override
        public String toString() {
            return label;
        }
    }

    private enum FitType {
        NONE("none", ""),
        ALL("all available data", "-f"),
        LIST("data matching observers list", "-ff");
        
        private final String label;
        private final String option;

        FitType(String label, String option) {
            this.label = label;
            this.option = option;
        }

        public String getOption() {
            return option;
        }
        
        @Override
        public String toString() {
            return label;
        }
    }
    
    private enum KeyPosition {
        TOPLEFT("top left",         "-k top_left_reverse_Left_invert"),
        TOPRIGHT("top right",       "-k top_right_Right_invert"),
        BOTTOMLEFT("bottom left",   "-k bottom_left_reverse_Left_invert"),
        BOTTOMRIGHT("bottom right", "-k bottom_right_Right_invert"),
        OFF("off", "-k off");
        
        private final String label;
        private final String option;
        
        KeyPosition(String label, String option) {
            this.label = label;
            this.option = option;
        }
        
        public String getOption() {
            return option;
        }
        
        @Override
        public String toString() {
            return label;
        }
    }
    
    /**
     * Initializes the controller class.
     */
    @Override
    public void initialize(URL url, ResourceBundle rb) {
        // fill combo boxes
        cbPlotType.getItems().setAll(PlotType.values());
        cbPlotType.getSelectionModel().select(PlotType.MAG);

        cbFitType.getItems().setAll(FitType.values());
        cbFitType.getSelectionModel().select(FitType.ALL);
        
        cbKeyPosition.getItems().setAll(KeyPosition.values());
        cbKeyPosition.getSelectionModel().select(KeyPosition.TOPLEFT);

        cbCurrentApparition.setSelected(true);

        paneLightCurve.setOnMouseClicked(event -> {
            labelWarning.setText("");
        });
        
        // obtaining prompt text for date inputs does not work as expected
        String pattern = ((SimpleDateFormat) DateFormat.getDateInstance(DateFormat.SHORT, Locale.getDefault())).toPattern();
        System.out.println("default pattern: " + pattern + " (current locale: " + Locale.getDefault() + ")");
        
        // set prompt text for date picker
        String lang = Locale.getDefault().getLanguage();
        switch (lang) {
            case "en":
                pattern="mm/dd/yyyy";
                break;
            case "de":
                pattern="dd.mm.yyyy";
                break;
            default:
                pattern="";
                break;
        }
        dpStart.setPromptText(pattern);
        dpEnd.setPromptText(pattern);
        
        // add listener to trigger action at end of aircliCmd (label changes from "Stop" to "Start")
        buttonStart.textProperty().addListener( (v, oldValue, newValue) -> {
            if (newValue.equals("Start")) {
                setButtonCOBSDataDisabledState(true);
            }
        });
        tfCometName.textProperty().addListener( (v, oldValue, newValue) -> {
            setButtonCOBSDataDisabledState(false);
        });
    }
    
    
    public void setReferences (ShellScript sh, SimpleLogger logger, StringProperty projectDir, StringProperty tempDir) {
        this.logger = logger;
        this.projectDir = projectDir;
        this.tempDir = tempDir;
        this.aircliCmd = new AirtoolsCLICommand(buttonStart, logger, sh);

        labelWarning.setText("");
        setButtonCOBSDataDisabledState(false);
    }
    

    private boolean isValidInputs() {
        String msg="";
        LocalDate ld;
        if (tfCometName.getText().isBlank()) {
            msg="ERROR: comet name is missing.";
            labelWarning.setText(msg);
            logger.log(msg);
            return false;
        }
        
        // format datepicker text entries
        if (! dpStart.getEditor().getText().isBlank()) {
            try {
                ld=dpStart.getConverter().fromString(dpStart.getEditor().getText());
                dpStart.setValue(ld);
            } catch (DateTimeParseException ex) {
                msg="ERROR: entered string of start date does not match date format.";
                labelWarning.setText(msg);
                logger.log(msg);
                return false;
            }
        } else dpStart.setValue(null);
        if (! dpEnd.getEditor().getText().isBlank()) {
            try {
                ld=dpEnd.getConverter().fromString(dpEnd.getEditor().getText());
                dpEnd.setValue(ld);
            } catch (DateTimeParseException ex) {
                msg="ERROR: entered string of end date does not match date format.";
                labelWarning.setText(msg);
                logger.log(msg);
                return false;
            }
        } else dpEnd.setValue(null);
        if (dpStart.getValue() != null && dpEnd.getValue() != null &&
                dpStart.getValue().isAfter(dpEnd.getValue())) {
            msg="ERROR: start date is after end date.";
            labelWarning.setText(msg);
            logger.log(msg);
            return false;
        }
        return true;
    }
    
    
    @FXML
    private void onButtonBrowseICQFile(ActionEvent event) {
        FileChooser fileChooser = new FileChooser();
        String dirName = "";
        
        if (! tfICQFile.getText().isBlank()) {
            File f = new File(tfICQFile.getText());
            dirName = f.getParent();
        }
        if (dirName.isBlank()) dirName = projectDir.getValue();
        if (dirName.isBlank()) dirName = System.getProperty("user.home");

        fileChooser.setInitialDirectory(new File(dirName));
        File file = fileChooser.showOpenDialog(this.paneLightCurve.getScene().getWindow());
        if (file.exists()) {
            tfICQFile.setText(file.getAbsolutePath());
        }
    }

    
    @FXML
    private void onDpStart(ActionEvent event) {
    }

    @FXML
    private void onDpEnd(ActionEvent event) {
    }

    
    public void setButtonCOBSDataDisabledState (boolean do_log) {
        File textFile = null;
        String comet = tfCometName.getText();
        String fileName = tempDir.getValue() + "/" + "tmp_cobs." + comet + ".icq";
        
        textFile = new File(fileName);
        if (textFile.exists()) {
            buttonCOBSData.setDisable(false);
        } else {
            if (do_log) logger.log("WARNING: file " + fileName + " not found");
            buttonCOBSData.setDisable(true);
        }
    }

    @FXML
    private void onButtonCOBSData(ActionEvent event) {
        System.out.println("LightCurveController: onButtonCOBSData()");
        String msg="";
        File textFile = null;
        String comet = tfCometName.getText();
        String tempFileName = tempDir.getValue() + "/" + "tmp_cobs." + comet + ".icq";
        String cobsFileName = "cobs." + comet + ".icq";
        
        textFile = new File(tempFileName);
        if (textFile.exists()) {
            try {
                Files.copy(Paths.get(tempFileName), Paths.get(projectDir.getValue() + "/" + cobsFileName), StandardCopyOption.COPY_ATTRIBUTES, StandardCopyOption.REPLACE_EXISTING);
                ProcessBuilder pb = new ProcessBuilder("/bin/bash", "-c", "mousepad " + projectDir.getValue() + "/" + cobsFileName);
                Process editorProcess = pb.start();
            } catch (IOException ex) {
                msg="WARNING: unable to start text viewer.";
                labelWarning.setText(msg);
                System.out.println(msg);
                Logger.getLogger(LightCurveController.class.getName()).log(Level.SEVERE, null, ex);
            }
        } else {
            msg="WARNING: missing COBS data file.";
            labelWarning.setText(msg);
            System.out.println(msg);
        }
    }


    @FXML
    private void onButtonStart(ActionEvent event) {
        System.out.println("LightCurveController: onButtonStart()");
        labelWarning.setText("");
        List<String> aircliCmdOpts = new ArrayList<>();
        List<String> aircliCmdArgs = new ArrayList<>();

        if (! isValidInputs()) return;
        PlotType plotType=cbPlotType.getSelectionModel().getSelectedItem();
        FitType fitType=cbFitType.getSelectionModel().getSelectedItem();
        KeyPosition keyPos=cbKeyPosition.getSelectionModel().getSelectedItem();

        // airfun function to call
        aircliCmdArgs.add(airfunFunc);
        
        // add options
        if (cbUseCOBS.isSelected())           aircliCmdArgs.add("-c");
        if (cbScanLocalProjects.isSelected()) aircliCmdArgs.add("-l");
        if (cbForceUpdate.isSelected())       aircliCmdArgs.add("-u");
        if (cbMPCModel.isSelected())          aircliCmdArgs.add("-m");
        if (cbDistance.isSelected())          aircliCmdArgs.add("-d");
        if (cbCurrentApparition.isSelected()) aircliCmdArgs.add("-ca");
        if (fitType != FitType.NONE)          aircliCmdArgs.add(fitType.getOption());
        if (keyPos  != KeyPosition.TOPLEFT)   aircliCmdArgs.add(keyPos.getOption());
        
        if (dpStart.getValue() != null || dpEnd.getValue() != null) {
            String str = "-x ";            
            DateTimeFormatter fmt = DateTimeFormatter.ofPattern("yyyyMMdd");
            if (dpStart.getValue() != null) {
                str += dpStart.getValue().format(fmt);
            }
            if (dpEnd.getValue() != null) {
                str += ":" + dpEnd.getValue().format(fmt);
            }
            aircliCmdArgs.add(str);
        }
        
        if (! tfModelM.getText().isBlank() && ! tfModelN.getText().isBlank()) {
            aircliCmdArgs.add("-n " + tfModelM.getText() + "," + tfModelN.getText());
        }
        
        if (! tfObsList.getText().isBlank()) {
            aircliCmdArgs.add("-i \"" + tfObsList.getText() + "\"");
        }
        
        if (! tfAddOptions.getText().isBlank()) {
            aircliCmdArgs.add(tfAddOptions.getText());
        }
        
        // add positional parameters
        aircliCmdArgs.add(tfCometName.getText());
        if (! tfICQFile.getText().isBlank()) {
            aircliCmdArgs.add(tfICQFile.getText());
        } else {
            aircliCmdArgs.add("\"\"");
        }
        aircliCmdArgs.add(plotType.name().toLowerCase());
        
        // run command
        System.out.println("cmd: " + aircliCmdOpts + " " + aircliTask + " " + aircliCmdArgs);
        //logger.log("# cmd: " + aircliCmdOpts + " " + aircliTask + " " + aircliCmdArgs);
        aircliCmd.setOpts(aircliCmdOpts.toArray(new String[0]));
        aircliCmd.setArgs(aircliCmdArgs.toArray(new String[0]));
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
