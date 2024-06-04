using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class CalibrateToFront : MonoBehaviour
{

    public Transform target;
    
    public float offset = 0;

    // Start is called before the first frame update
    void Start()
    {
        CalculateOffset();
    }

    // Update is called once per frame
    void LateUpdate()
    {
        UpdateEuler();
    }

    public void CalculateOffset()
	{
        Vector3 offsetVector = transform.eulerAngles - target.eulerAngles;

        offset += offsetVector.y;


        Debug.Log("offset x:" + offsetVector.x + " y: " + offsetVector.y + " y: " + offsetVector.z);
    }

    void UpdateEuler()
    {
        Vector3 r = transform.eulerAngles;

        r.y = transform.eulerAngles.y - offset;
        transform.eulerAngles = r;

       // transform.rotation *= Quaternion.Euler(x, 0f, 0f);

    }
}
