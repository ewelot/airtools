package tl.airtoolsgui.controller;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.IOException;
import java.net.URL;
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
import javafx.beans.value.ObservableValue;
import javafx.collections.FXCollections;
import javafx.event.ActionEvent;
import javafx.fxml.FXML;
import javafx.fxml.Initializable;
import javafx.scene.Node;
import javafx.scene.control.Button;
import javafx.scene.control.CheckBox;
import javafx.scene.control.ChoiceBox;
import javafx.scene.control.ComboBox;
import javafx.scene.control.Label;
import javafx.scene.control.TextField;
import javafx.scene.layout.AnchorPane;
import javafx.stage.FileChooser;
import javafx.stage.Stage;
import tl.airtoolsgui.model.AirtoolsCLICommand;
import tl.airtoolsgui.model.ImageSet;
import tl.airtoolsgui.model.ShellScript;
import tl.airtoolsgui.model.SimpleLogger;

/**
 * FXML Controller class
 *
 * @author lehmann
 */
public class WCSCalibController implements Initializable {

    @FXML
    private AnchorPane paneWCSCalib;
    @FXML
    private ChoiceBox<ImageSet> cbImageSet;
    @FXML
    private Button buttonGuessWCSParam;
    @FXML
    private TextField tfRA;
    @FXML
    private TextField tfDEC;
    @FXML
    private ComboBox<NorthPA> cbNorth;
    @FXML
    private ChoiceBox<String> cbCatalog;
    @FXML
    private Button buttonBrowseMask;
    @FXML
    private TextField tfMask;
    @FXML
    private TextField tfMagLim;
    @FXML
    private TextField tfMinSN;
    @FXML
    private TextField tfCrossRadius;
    @FXML
    private ChoiceBox<String> cbDegree;
    @FXML
    private CheckBox cbShowPlots;
    @FXML
    private TextField tfExpert;
    @FXML
    private CheckBox cbDelete;
    @FXML
    private Label labelWarning;
    @FXML
    private Button buttonStart;
    @FXML
    private Button buttonCancel;
    
    private SimpleLogger logger;
    private StringProperty projectDir = new SimpleStringProperty();
    private StringProperty tempDir = new SimpleStringProperty();
    private ShellScript sh;
    private AirtoolsCLICommand aircliCmd;
    private final String aircliTask = "usercmd";
    private final String airfunFunc = "AIwcs";

    private final List<ImageSet> imageSetList = new ArrayList<>();

    private enum NorthPA {
        PA0(    0, "north up"),
        PA90(  90, "north left"),
        PA180(180, "north down"),
        PA270(270, "north right")
        ;
        
        private final int pa;
        private final String direction;

        NorthPA(int pa, String direction) {
            this.pa = pa;
            this.direction = direction;
        }

        NorthPA(int pa) {
            this.pa = pa;
            this.direction = "";
        }

        public int getPA() {
            return pa;
        }
        
        @Override
        public String toString() {
            if (direction.isBlank()) return Integer.toString(pa);
            return Integer.toString(pa) + " - " + direction;
        }
    }


    /**
     * Initializes the controller class.
     */
    @Override
    public void initialize(URL url, ResourceBundle rb) {
        labelWarning.setText("");

        // add combobox items
        cbNorth.getItems().setAll(NorthPA.values());
        cbDegree.getItems().addAll("2", "3", "4", "5");
        cbDegree.getSelectionModel().select(1);
        cbCatalog.getItems().addAll("GAIA-EDR3", "UCAC-4", "2MASS", "PPMX");
        cbCatalog.getSelectionModel().select(1);

        tfMask.focusedProperty().addListener((c, oldValue, newValue) -> {
            Platform.runLater(() -> {
                //tfMask.deselect();
                tfMask.end();
            });
        });
    }    

    public void setReferences (ShellScript sh, SimpleLogger logger, StringProperty projectDir, StringProperty tempDir) {
        this.logger = logger;
        this.projectDir = projectDir;
        this.sh = sh;
        this.aircliCmd = new AirtoolsCLICommand(buttonStart, logger, sh);
        this.tempDir = tempDir;
        
        populateChoiceBoxImageSet();

        cbImageSet.getSelectionModel().selectedItemProperty().addListener((v, oldValue, newValue) -> {
            System.out.println("selected set: " + newValue);
            //logger.log("selected set: " + newValue);
            setDefaultValues();
        });
        
        paneWCSCalib.setOnMouseClicked(event -> {
            labelWarning.setText("");
        });
    }

    public void updateImageSetList () {
        // must be called by project change
        System.out.println("WCSCalibController: updateImageSetList");
        File inFile = new File(projectDir.getValue() + "/set.dat");
        if (inFile.exists() && inFile.isFile()) {
            final List<ImageSet> oldImageSetList = new ArrayList<>(imageSetList);
            setImageSetList();
            if (! imageSetList.equals(oldImageSetList)) {
                populateChoiceBoxImageSet();
            
                // TODO: try to keep originally selected ImageSet
                // TODO: if selected ImageSet differs from old one then run
                cbImageSet.getSelectionModel().selectFirst();
            }
        } else {
            setDefaultValues();
        }
    }
    

    private void populateChoiceBoxImageSet() {
        System.out.println("WCSCalibController: populateChoiceBoxImageSet()");
        setImageSetList();
        cbImageSet.setItems(FXCollections.observableArrayList(
            imageSetList));
        cbImageSet.getSelectionModel().selectFirst();
    }


    private void setImageSetList () {
        System.out.println("WCSCalibController: setImageSetList");
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
    
    

    public void resetValues() {
        /* reset widgets when the dialog window is shown again (same image set) */     
        cbDelete.setSelected(false);        
    }


    private void setDefaultValues() {
        // set default values in GUI widgets when new image set is selected
        
        // update widgets to their defaults
        tfRA.setText("");
        tfDEC.setText("");
        cbNorth.getEditor().setText("");
        //cbCatalog.getSelectionModel().select(1);
        tfMask.setText("");
        tfMagLim.setText("");
        tfMinSN.setText("");
        tfCrossRadius.setText("");
        cbDegree.getSelectionModel().select(1);
        cbShowPlots.setSelected(true);

        tfExpert.setText("");
        cbDelete.setSelected(false);
    }
    
    
    public void updateValues(String resultString) {
        /* update widgets with values parsed from resultString (output of guess_wcscalib) */
        System.out.println("WCSCalibController: updateValues(resultString)");
        String[] columns = resultString.split("[ ]+");
        if (columns.length >= 6) {
            // Note: does require telid in field 11
            if (! columns[0].equals("-")) tfRA.setText(columns[0]);          else tfRA.setText("");
            if (! columns[1].equals("-")) tfDEC.setText(columns[1]);         else tfDEC.setText("");
            if (! columns[2].equals("-")) cbNorth.getEditor().setText(columns[2]); else cbNorth.getEditor().setText("");
            if (! columns[3].equals("-")) tfMagLim.setText(columns[3]);      else tfMagLim.setText("");
            if (! columns[4].equals("-")) tfMinSN.setText(columns[4]);       else tfMinSN.setText("");
            if (! columns[5].equals("-")) tfCrossRadius.setText(columns[5]); else tfCrossRadius.setText("");
        } else {
            labelWarning.setText("ERROR parsing output from guess_wcsparam.");
        }
        tfMask.setText("");
        tfExpert.setText("");
        cbDelete.setSelected(false);        
    }



    @FXML
    private void onButtonGuessWCSParam(ActionEvent event) {
        System.out.println("WCSCalibController: onButtonGuessWCSParam()");
        labelWarning.setText("");

        BooleanProperty cmdIsRunning = new SimpleBooleanProperty();
        AirtoolsCLICommand aUserCmd = new AirtoolsCLICommand((Button) event.getSource(), logger, sh, cmdIsRunning);
        List<String> aircliCmdOpts = new ArrayList<>();
        List<String> aircliCmdArgs = new ArrayList<>();

        cmdIsRunning.setValue(Boolean.TRUE);
        cmdIsRunning.addListener((obs, oldValue, newValue) -> {
            if (! newValue) {
                int exitCode = aUserCmd.getExitCode();
                System.out.println("command has finished with exit code " + exitCode);
                if (aUserCmd.getExitCode() != 0)
                    labelWarning.setText("ERROR: guess_wcsparam has failed (" + exitCode + ").");
                else
                    updateValues(aUserCmd.getResultString());
            }
        });

        aircliCmdArgs.add("guess_wcsparam");
        aircliCmdArgs.add(cbImageSet.getSelectionModel().getSelectedItem().getSetname());
        aUserCmd.setOpts(aircliCmdOpts.toArray(String[]::new));
        aUserCmd.setArgs(aircliCmdArgs.toArray(String[]::new));
        aUserCmd.run();
    }
    
    
    @FXML
    private void onButtonBrowseMask(ActionEvent event) {
        System.out.println("WCSCalibController: onButtonBrowseMask()");
        FileChooser fileChooser = new FileChooser();
        String fileName = tfMask.getText();
        File pdir = new File(projectDir.getValue());
        
        if (fileName.isEmpty()) {
            fileChooser.setInitialDirectory(pdir);
        } else {
            File f = new File(fileName);
            fileChooser.setInitialDirectory(f.getParentFile());
            fileChooser.setInitialFileName(fileName);
        }
        fileChooser.getExtensionFilters().addAll(
            new FileChooser.ExtensionFilter("Region Files", "*.reg", "*.ds9")
        );

        Stage stage = (Stage) paneWCSCalib.getScene().getWindow();
        File selectedFile = fileChooser.showOpenDialog(stage);
        if (selectedFile != null) {
            String fullName = selectedFile.getAbsolutePath();
            if (fullName.startsWith(projectDir.getValue())) {
                tfMask.setText(fullName.substring(projectDir.getValue().length()));
            } else {
                tfMask.setText(selectedFile.getAbsolutePath());
                tfMask.end();
            }
        }
    }

    
    private boolean isValidInputs() {
        String msg="";
        // TODO: Check for valid coordinate strings
        // TODO: Check for valid region mask file name
        if (! tfCrossRadius.getText().isBlank()) {
            double val=-1;
            try {
                val=Double.parseDouble(tfCrossRadius.getText());
            } catch (Exception e) {
                msg="ERROR: invalid CrossID radius.";
                labelWarning.setText(msg);
                logger.log(msg);
                return false;
            }
            if (val<1 || val>100) {
                msg="ERROR: value of CrossID radius out of limits (1..100).";
                labelWarning.setText(msg);
                logger.log(msg);
                return false;
            }
        }
        return true;
    }

    @FXML
    private void onButtonStart(ActionEvent event) {
        System.out.println("WCSCalibController: onButtonStart()");
        labelWarning.setText("");
        List<String> aircliCmdOpts = new ArrayList<>();
        List<String> aircliCmdArgs = new ArrayList<>();

        if (! isValidInputs()) return;
        
        //FitType fitType=cbFitType.getSelectionModel().getSelectedItem();

        // airfun function to call
        aircliCmdArgs.add(airfunFunc);
        aircliCmdArgs.add("-q");
        
        // add options
        if (cbShowPlots.isSelected())           aircliCmdArgs.add("-s");
        //if (fitType != FitType.NONE)          aircliCmdArgs.add(fitType.getOption());
        
        if (! tfRA.getText().isBlank() && ! tfDEC.getText().isBlank()) {
            aircliCmdArgs.add("-c " + tfRA.getText() + " " + tfDEC.getText());
        }

        
        // next line does throw an error:
        //  java.lang.ClassCastException: class java.lang.String cannot be cast to class tl.airtoolsgui.controller.WCSCalibController$NorthPA
        //NorthPA npa = cbNorth.getSelectionModel().getSelectedItem();
        String sNorthPA = cbNorth.getEditor().getText().stripLeading().replaceAll(" .*", "");
        
        if (! sNorthPA.isBlank()) {
            double north=0;
            try {
                north=Double.parseDouble(sNorthPA);
                aircliCmdArgs.add("-n " + north);
            } catch (Exception e) {
                logger.log("WARNING: unable to parse north value.");
                labelWarning.setText("WARNING: unable to parse north value.");
            }
        }
        
        if (! tfMask.getText().isBlank()) {
            aircliCmdArgs.add("-m " + tfMask.getText());
        }
        
        if (! tfCrossRadius.getText().isBlank()) {
            aircliCmdArgs.add("-cr " + tfCrossRadius.getText());
        }
        
        aircliCmdArgs.add("-d " + cbDegree.getSelectionModel().getSelectedItem());
        
        if (! tfExpert.getText().isBlank()) {
            aircliCmdArgs.add(tfExpert.getText());
        }

        // add mandatory positional parameters
        aircliCmdArgs.add(cbImageSet.getSelectionModel().getSelectedItem().getSetname());
        aircliCmdArgs.add(cbCatalog.getSelectionModel().getSelectedItem().toLowerCase());
        if (! tfMagLim.getText().isBlank()) {
            aircliCmdArgs.add(tfMagLim.getText());
        } else {
            aircliCmdArgs.add("\"\"");
        }
        if (! tfMinSN.getText().isBlank()) {
            aircliCmdArgs.add(tfMinSN.getText());
        } else {
            aircliCmdArgs.add("\"\"");
        }
        
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
