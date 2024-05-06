using System.Collections.Generic;
using UnityEngine;
using TsAPI.Types;
using UnityEngine.UI;
using TMPro;
using Newtonsoft.Json;
using System;

public class TrainingManager : MonoBehaviour
{
    //Model Setting Panel
    [SerializeField]
    private Dropdown algorithmDropDownModel;
    [SerializeField]
    private Dropdown exerciseTypeDropDownModel;
    [SerializeField]
    private TMP_InputField subjectIDsInput;
    [SerializeField]
    private TMP_InputField measurementSetsInput;
    [SerializeField]
    private Toggle validationToggle;
    [SerializeField]
    private GameObject modelSettingPanel;

    public TsHumanAnimator tsHumanAnimator;

    private DataGateway dataGateway;


    void Start()
    {
        dataGateway = FindObjectOfType<DataGateway>();

        FillExerciseTypeDropDownModel();
        FillAlgorithmDropDownModel();
    }

    void Update()
    {
        
    }

    void FillExerciseTypeDropDownModel()
    {
        string[] names = Enum.GetNames(typeof(ExerciseType));
        exerciseTypeDropDownModel.ClearOptions();
        exerciseTypeDropDownModel.AddOptions(new List<string>(names));
    }

    void FillAlgorithmDropDownModel()
    {
        string[] names = Enum.GetNames(typeof(Algorithm));
        algorithmDropDownModel.ClearOptions();
        algorithmDropDownModel.AddOptions(new List<string>(names));
    }

    public void TrainModel()
    {
        if (subjectIDsInput.text == string.Empty)
        {
            Debug.LogError("Please enter subject id(s)");
            return;
        } else
        {
            Algorithm algorithm = (Algorithm)Enum.Parse(typeof(Algorithm), algorithmDropDownModel.options[algorithmDropDownModel.value].text);
            ExerciseType exerciseType = (ExerciseType)Enum.Parse(typeof(ExerciseType), exerciseTypeDropDownModel.options[exerciseTypeDropDownModel.value].text);
            ModelDataObject modelDataObject = new ModelDataObject(subjectIDsInput.text, exerciseType, algorithm, measurementSetsInput.text);
            dataGateway.TrainModel(modelDataObject, validationToggle.isOn);
        }
    }

    public void Cancel()
    {
        modelSettingPanel.SetActive(true);
    }
}
