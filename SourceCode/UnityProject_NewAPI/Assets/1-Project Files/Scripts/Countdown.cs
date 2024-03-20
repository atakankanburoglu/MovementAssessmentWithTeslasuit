using System.Collections;
using UnityEngine.UI;
using UnityEngine;
using UnityEngine.SceneManagement;
using TMPro;

public class Countdown : MonoBehaviour
{

    public float timeLeft = 3.0f;
    public bool counting = false;

    [SerializeField]
    private Text counter;

    void Update()
    {
        if (counting)
        {
            timeLeft -= Time.deltaTime;
            counter.text = (timeLeft).ToString("0");
        }
        if(timeLeft < 0)
        {
            ResetCounter();
        }
    }

    public void ResetCounter()
    {
        timeLeft = 3.0f;
        counting = false;
        counter.gameObject.SetActive(false);
    }

    public void StartCounter()
    {
        counting = true;
        counter.gameObject.SetActive(true);
    }
}