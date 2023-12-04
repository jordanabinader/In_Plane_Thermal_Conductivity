import React from 'react';
import styles from './Loader.module.css'; 

const FullPageLoader = () => {
  return (
    <div className={styles.fullPageLoader}>
        <div>Setting test up...</div>
        <span className="loading loading-infinity loading-lg"></span>
    </div>
  );
};

export default FullPageLoader;
