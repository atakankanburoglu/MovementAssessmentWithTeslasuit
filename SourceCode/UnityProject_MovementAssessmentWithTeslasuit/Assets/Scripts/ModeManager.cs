using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using System;

public class ModeManager : MonoBehaviour
{
    //Sample Setting Panel
    [SerializeField]
    private Dropdown modeDropdown;
    [SerializeField]
    private GameObject recordingUI;
    [SerializeField]
    private GameObject replayUI;
    [SerializeField]
    private GameObject trainingUI;
    [SerializeField]
    private GameObject testingUI;
    [SerializeField]
    private GameObject feedbackUI;
    [SerializeField]
    private GameObject cancelButton;

    public TestingManager testingManager;

    void Start()
    {
        FillModeDropDown();
    }
   
    void FillModeDropDown()
    {
        string[] names = Enum.GetNames(typeof(ApplicationMode));
        modeDropdown.ClearOptions();
        modeDropdown.AddOptions(new List<string>(names));
    }

    public void OptionChosenFromDropDown()
    {
        ApplicationMode mode = (ApplicationMode)Enum.Parse(typeof(ApplicationMode), modeDropdown.options[modeDropdown.value].text);
        if (mode == ApplicationMode.Recording)
        {
            recordingUI.SetActive(true);
            replayUI.SetActive(false);
            trainingUI.SetActive(false);
            testingUI.SetActive(false);
            feedbackUI.SetActive(false);
            cancelButton.SetActive(true);
        }
        else if (mode == ApplicationMode.Replay)
        {
            recordingUI.SetActive(false);
            replayUI.SetActive(true);
            trainingUI.SetActive(false);
            testingUI.SetActive(false);
            feedbackUI.SetActive(false);
            cancelButton.SetActive(true);
        }
        else if (mode == ApplicationMode.Training)
        {
            recordingUI.SetActive(false);
            replayUI.SetActive(false);
            trainingUI.SetActive(true);
            testingUI.SetActive(false);
            feedbackUI.SetActive(false);
            cancelButton.SetActive(true);
        }
        else if (mode == ApplicationMode.Testing)
        {
            recordingUI.SetActive(false);
            replayUI.SetActive(false);
            trainingUI.SetActive(false);
            testingUI.SetActive(true);
            feedbackUI.SetActive(false);
            cancelButton.SetActive(true);
        }
        else if (mode == ApplicationMode.Feedback)
        {
            recordingUI.SetActive(false);
            replayUI.SetActive(false);
            trainingUI.SetActive(false);
            testingUI.SetActive(false);
            feedbackUI.SetActive(true);
            cancelButton.SetActive(true);
        }
        else
        {
            CancelAllAction();
        }
    }

    public void CancelAllAction()
    {
        recordingUI.SetActive(false);
        replayUI.SetActive(false);
        trainingUI.SetActive(false);
        testingUI.SetActive(false);
        feedbackUI.SetActive(false);
        cancelButton.SetActive(false);
        FillModeDropDown();
    }
}
