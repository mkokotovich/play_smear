import React, { useEffect  } from 'react';

const AdsComponent = (props) => {
    const { dataAdSlot } = props;  

    useEffect(() => {
        try {
            (window.adsbygoogle = window.adsbygoogle || []).push({});
        }
        catch (e) {
        }
    },[]);

    return (
      <>
        <p style={{fontSize: "0.8em"}}>The following are ads to help pay for the operation of the site:</p>
        <ins className="adsbygoogle"
          style={{ display: "block" }}
          data-ad-client="ca-pub-3354368836279808"
          data-ad-slot={dataAdSlot}
          data-ad-format="auto"
          data-full-width-responsive="true">
        </ins>
      </>
    );
};

export default AdsComponent;
